-- Encrypted saved plans for the retirement planners (retire-qc, retire-on, later retire-personal).
-- One row per saved plan. `blob` is ciphertext made in the browser; the server never sees a plan.
-- Rows belong to one user and are only usable while that user still has access to the app.
-- Give this to the Supabase AI assistant as a prompt (see README), then run supabase-platform- audit.sql.

create table if not exists public.planner_profiles (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  app         text not null check (app in ('retire-qc','retire-on','retire-personal')),
  blob        text not null check (length(blob) between 50 and 300000),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index if not exists planner_profiles_user_app_idx on public.planner_profiles (user_id, app);

alter table public.planner_profiles enable row level security;

drop policy if exists planner_profiles_select on public.planner_profiles;
drop policy if exists planner_profiles_insert on public.planner_profiles;
drop policy if exists planner_profiles_update on public.planner_profiles;
drop policy if exists planner_profiles_delete on public.planner_profiles;
create policy planner_profiles_select on public.planner_profiles for select to authenticated
  using (user_id = auth.uid() and public.has_app_access(app));
create policy planner_profiles_insert on public.planner_profiles for insert to authenticated
  with check (user_id = auth.uid() and public.has_app_access(app));
create policy planner_profiles_update on public.planner_profiles for update to authenticated
  using (user_id = auth.uid() and public.has_app_access(app))
  with check (user_id = auth.uid() and public.has_app_access(app));
create policy planner_profiles_delete on public.planner_profiles for delete to authenticated
  using (user_id = auth.uid() and public.has_app_access(app));

-- Data API grants (explicit; nothing for anon/public)
revoke all on public.planner_profiles from anon, public;
grant select, insert, update, delete on public.planner_profiles to authenticated;

create or replace function public.planner_profiles_touch() returns trigger
language plpgsql set search_path = public, pg_temp as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists planner_profiles_touch on public.planner_profiles;
create trigger planner_profiles_touch before update on public.planner_profiles
  for each row execute function public.planner_profiles_touch();
