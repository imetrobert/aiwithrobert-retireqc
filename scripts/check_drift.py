#!/usr/bin/env python3
"""Warn when the copied code in the sibling planner repos has drifted apart.

account.js lives in three repos (Quebec, Ontario, personal) and statements.js in two
(Quebec = personal; Ontario has its own). They are copies kept in step by hand.
This fetches the siblings from GitHub and checks:
  1. statements.js here is byte-identical to the personal planner's.
  2. account.js has the same set of functions in all three repos.
Network trouble skips the check (exit 0); a real difference exits 1 and prints it.
Run it from the Quebec repo (CI does this in the Checks workflow).
"""
import re, sys, urllib.request

RAW = 'https://raw.githubusercontent.com/imetrobert/%s/main/%s'
HERE = {'account.js': open('account.js', encoding='utf-8').read(),
        'statements.js': open('statements.js', encoding='utf-8').read()}

def get(repo, path):
    try:
        with urllib.request.urlopen(RAW % (repo, path), timeout=20) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        print('SKIP: could not fetch %s/%s (%s)' % (repo, path, e)); sys.exit(0)

def funcs(src):
    return set(re.findall(r'function\s+([A-Za-z0-9_$]+)\s*\(', src))

bad = []
if get('imetrobert-retire', 'statements.js') != HERE['statements.js']:
    bad.append('statements.js differs between aiwithrobert-retireqc and imetrobert-retire (they should be identical)')
mine = funcs(HERE['account.js'])
for repo in ('aiwithrobert-retireon', 'imetrobert-retire'):
    other = funcs(get(repo, 'account.js'))
    if other != mine:
        bad.append('account.js functions differ in %s: only here %s; only there %s' % (repo, sorted(mine - other), sorted(other - mine)))
for b in bad:
    print('FAIL:', b)
print('OK: shared planner code is in step' if not bad else 'Drift found: apply the same fix in the other repo(s).')
sys.exit(1 if bad else 0)
