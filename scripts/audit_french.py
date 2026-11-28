"""French audit of the Quebec planner (not run by CI; needs `pip install playwright` and `playwright install chromium`).
Usage: python3 scripts/audit_french.py
Opens the planner at ?lang=fr with a stubbed sign-in server, walks every step, popup, results view and several
scenarios, and prints any text that still looks English. The 'Switch to English' button is meant to stay English.
Fix a hit by adding an EXACT entry or a P.push pattern near the end of index.html (see docs/common-edits.md, French gotchas)."""
import http.server, threading, json, os, re, sys, functools
from playwright.sync_api import sync_playwright
ROOT=sys.argv[1] if len(sys.argv)>1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB='https://ipnajvgwtjrlecbqfwrh.supabase.co'
def handler(route, request):
    cors={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'}
    if request.method=='OPTIONS': return route.fulfill(status=204,headers=cors)
    url=request.url; body=json.loads(request.post_data) if request.post_data else None
    def send(s,d=None): route.fulfill(status=s,headers=dict(cors,**{'content-type':'application/json'}),body=json.dumps(d) if d is not None else '')
    if 'grant_type=password' in url: return send(200,{'access_token':'tok-t@e.com','refresh_token':'ref-t@e.com','expires_in':3600,'user':{'email':'t@e.com'}})
    if 'grant_type=refresh_token' in url: return send(200,{'access_token':'tok-t@e.com','refresh_token':'ref-t@e.com','expires_in':3600,'user':{'email':'t@e.com'}})
    if '/rpc/has_app_access' in url: return send(200,True)
    if '/rest/v1/planner_profiles' in url: return send(200,[])
    return send(404,{})
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Q,directory=ROOT)); threading.Thread(target=srv.serve_forever,daemon=True).start()
URL='http://127.0.0.1:%d/index.html'%srv.server_address[1]
EN=set('the your you is are this that with will from not can to and for of if it at by be was were has have been into than then when which what who how our we they their its'.split())
FRW=set('le la les des une un du de et est pour sur avec votre vos vous que qui dans par pas ce cette ces au aux se sont plus ou'.split())
def looks_en(s):
    w=re.findall(r"[A-Za-z']+",s.lower())
    if len(w)<2: return False
    en=sum(1 for x in w if x in EN); fr=sum(1 for x in w if x in FRW)
    return en>=1 and en>fr
JS="""()=>{const out=[];const skip=new Set(['SCRIPT','STYLE','NOSCRIPT','TEMPLATE']);
function walk(n,path){ if(n.nodeType===3){const t=n.nodeValue.replace(/\\s+/g,' ').trim(); if(t) out.push(['text',t,path]); return;}
 if(n.nodeType!==1||skip.has(n.tagName))return;
 for(const a of ['placeholder','title','aria-label','alt']){const v=n.getAttribute&&n.getAttribute(a); if(v) out.push([a,v,n.tagName+'#'+n.id]);}
 if((n.tagName==='INPUT'&&/button|submit/.test(n.type))&&n.value) out.push(['value',n.value,n.id]);
 for(const c of n.childNodes) walk(c,(n.id?'#'+n.id:n.tagName.toLowerCase()));}
walk(document.body,'body');return out}"""
seen={}
weak={}
def collect(page,label):
    for kind,t,p in page.evaluate(JS):
        w=re.findall(r"[A-Za-z']+",t)
        if len(w)>=3 and not re.search(r"[àâçéèêëîïôûùüœÀÉ]",t) and not any(x.lower() in FRW for x in w) and not looks_en(t) and t not in weak and not re.fullmatch(r"[\W\d_A-Z]+",t): weak[t]=(label,kind,p)
    _collect(page,label)
def _collect(page,label):
    for kind,t,p in page.evaluate(JS):
        if looks_en(t) and t not in seen: seen[t]=(label,kind,p)
def setv(page,i,v):
    page.evaluate("([i,v])=>{const e=document.getElementById(i);if(!e)return;if(e.type==='checkbox'){e.checked=!!v}else{e.value=v};e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}",[i,v])
with sync_playwright() as pw:
    try: br=pw.chromium.launch(channel='chrome')
    except Exception: br=pw.chromium.launch()
    ctx=br.new_context(viewport={'width':390,'height':844}); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)))
    ctx.route(SB+'/**',handler)
    page.goto(URL+'?lang=fr'); page.wait_for_selector('#awr-gate')
    collect(page,'gate')
    page.fill('#awr-email','t@e.com'); page.fill('#awr-pw','pw-ok'); page.click('#awr-gate button[type=submit]')
    page.wait_for_function('window.awrCloudReady===true'); page.wait_for_timeout(600)
    collect(page,'after sign-in (start FR)')
    page.click('#menuBtn'); page.wait_for_timeout(300); collect(page,'menu')
    page.click('#menuBtn')
    # open all details
    page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); page.wait_for_timeout(300)
    collect(page,'step1 details')
    # info popups
    def popups(label):
        n=page.evaluate("document.querySelectorAll('.info-btn').length")
        for i in range(n):
            try:
                page.evaluate("(i)=>document.querySelectorAll('.info-btn')[i].click()",i); page.wait_for_timeout(120)
                txt=page.evaluate("(document.getElementById('infoSheet')||{}).innerText||''")
                for line in re.split(r'\n+',txt):
                    if looks_en(line) and line not in seen: seen[line]=(label+' popup %d'%i,'popup','')
                page.evaluate("document.querySelectorAll('#infoSheet button, .info-close').forEach(b=>b.click())")
            except Exception as e: pass
    steps=[1,2,3,4,5,6]
    for s in [1,2,3]:
        page.evaluate("(s)=>showStep(s)",s); page.wait_for_timeout(300)
        page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true);document.querySelectorAll('.asset-row.collapsible').forEach(c=>c.classList.remove('collapsed'))")
        collect(page,'step%d'%s); popups('step%d'%s)
    # couple mode + calculate
    for mode in ['single','couple']:
        page.evaluate("(m)=>{const c=document.getElementById('calcMode');c.value=m;c.dispatchEvent(new Event('change'))}",mode); page.wait_for_timeout(300)
        for s in [1,2]:
            page.evaluate("(s)=>showStep(s)",s); page.wait_for_timeout(200)
            page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true);document.querySelectorAll('.asset-row.collapsible').forEach(c=>c.classList.remove('collapsed'))")
            collect(page,mode+' step%d'%s)
        try:
            page.evaluate("calculateRetirementPlan()"); page.wait_for_timeout(2500)
        except Exception as e: errs.append('calc '+str(e))
        page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); page.wait_for_timeout(300)
        collect(page,mode+' results'); popups(mode+' results')
        # click each tab / view toggle
        page.evaluate("document.querySelectorAll('.seg button, .tabs button, [role=tab]').forEach(b=>{try{b.click()}catch(e){}})"); page.wait_for_timeout(400)
        page.evaluate("document.querySelectorAll('.yp-card, .year-card, .yp-head').forEach((c,i)=>{if(i<6)try{c.click()}catch(e){}})"); page.wait_for_timeout(300)
        collect(page,mode+' results views')
    # other screens
    for fn,lab in [("openExpenses()",'expenses'),("typeof evOpen==='function'&&evOpen(0)",'life events'),("showStep(5)",'saved'),("showStep(6)",'tax rules')]:
        try:
            page.evaluate(fn); page.wait_for_timeout(500)
            page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            collect(page,lab); popups(lab)
        except Exception as e: errs.append(lab+' '+str(e)[:80])
    # dialogs
    for fn,lab in [("askSaveChoice('x',function(){},'y')",'save dialog')]:
        try: page.evaluate(fn); page.wait_for_timeout(300); collect(page,lab)
        except Exception as e: errs.append(lab+' '+str(e)[:80])
    # cloud panel
    try:
        page.evaluate("document.querySelectorAll('#infoSheet,.save-choice,.ask-save,[id*=askSave],[class*=overlay],[class*=modal]').forEach(e=>{try{e.remove()}catch(x){}})")
        page.evaluate("showStep(1)")
        page.evaluate("awrOpenCloud()"); page.wait_for_selector('#awr-p1',timeout=5000); collect(page,'cloud panel (passphrase)')
        page.fill('#awr-p1','correct horse battery'); page.fill('#awr-p2','correct horse battery'); page.evaluate("document.querySelector('#awr-panel .awr-btn').click()"); page.wait_for_timeout(900); collect(page,'cloud panel (list)')
    except Exception as e: errs.append('cloud '+str(e)[:80])
    # ---- extra scenarios (deficit, events, DB pension, unlock, retired, couple, invalid input)
    try:
        page.evaluate("showStep(1)")
        def run(label,sets,calc=True):
            for i,v in sets: setv(page,i,v)
            page.evaluate("showStep(1)"); page.wait_for_timeout(200)
            page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            collect(page,label+' form')
            if calc:
                try: page.evaluate("calculateRetirementPlan()"); page.wait_for_timeout(2500)
                except Exception as e: errs.append(label+' '+str(e)[:80])
                page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
                collect(page,label+' results')
                page.evaluate("document.querySelectorAll('.seg button,[role=tab]').forEach(b=>{try{b.click()}catch(e){}})"); page.wait_for_timeout(300)
                page.evaluate("document.querySelectorAll('.yp-card,.year-card,.yp-head').forEach((c,i)=>{if(i<40)try{c.click()}catch(e){}})"); page.wait_for_timeout(300)
                collect(page,label+' views')
                n=page.evaluate("document.querySelectorAll('.info-btn').length")
                for i in range(min(n,60)):
                    try:
                        page.evaluate("(i)=>document.querySelectorAll('.info-btn')[i].click()",i); page.wait_for_timeout(80)
                        txt=page.evaluate("(document.getElementById('infoSheet')||{}).innerText||''")
                        for line in re.split(r'\n+',txt):
                            if looks_en(line) and line not in seen: seen[line]=(label+' popup','popup','')
                        page.evaluate("document.querySelectorAll('#infoSheet button').forEach(b=>b.click())")
                    except Exception: pass
        run('deficit',[('currentAge','60'),('spendAmount','15000'),('liraBalance','20000')])
        run('events',[('spendAmount','3000'),('event1Name','Voyage'),('event1Amount','8000'),('event1Age','68'),('event2Name','Toit'),('event2Amount','20000'),('event2Age','72')])
        run('db pension',[('pensionType','db'),('ownPensionAnnual','30000'),('ownPensionStartAge','60')])
        run('federal unlock',[('pensionType','dc'),('liraJurisdiction','federal'),('liraBalance','300000'),('rlifUnlockEnabled',True),('rlifUnlockAge','60')])
        run('already retired',[('alreadyRetired',True)])
        run('couple db',[('alreadyRetired',False),('calcMode','couple'),('spouseAge','58')])
        try: page.evaluate("hhSwitch('sp')"); page.wait_for_timeout(300); run('spouse form',[],calc=False)
        except Exception as e: errs.append('hh '+str(e)[:80])
        # invalid input -> error messages
        page.evaluate("hhSwitch('me')"); 
        for bad in [('currentAge',''),('currentAge','200'),('targetAge','10')]:
            setv(page,*bad)
            try: page.evaluate("calculateRetirementPlan()"); page.wait_for_timeout(600)
            except Exception as e: pass
            collect(page,'invalid '+bad[0]+'='+bad[1])
            page.evaluate("document.querySelectorAll('dialog,.toast,.err').forEach(e=>{})")
    except Exception as e: errs.append('scenarios '+str(e)[:80])
    br.close()
print('ENGLISH-LOOKING TEXT IN FRENCH MODE: %d'%len(seen))
for t,(lab,kind,p) in sorted(seen.items(),key=lambda x:x[1][0]): print('[%s|%s] %s'%(lab,kind,t[:170]))
print('\nWEAK (no French marker, >=3 words): %d'%len(weak))
for t,(lab,kind,p) in sorted(weak.items(),key=lambda x:x[1][0]): print('[%s|%s] %s'%(lab,kind,t[:140]))
print('ERRORS:',errs[:6])
sys.exit(1 if [t for t in seen if t!='Switch to English'] else 0)
