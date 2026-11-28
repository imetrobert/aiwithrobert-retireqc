"""Retakes the guide screenshots from the current index.html (phone size) into docs/guide/img/<lang>/.
Run by the "Guide screenshots" workflow; locally: pip install playwright; python3 -m playwright install chromium; python3 scripts/make_guide_shots.py"""
import os,sys,subprocess
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
if len(sys.argv)==1:
    langs=['en']+(['fr'] if os.path.exists(os.path.join(ROOT,'docs','guide','fr.md')) else [])
    for l in langs: subprocess.check_call([sys.executable,__file__,ROOT,l,os.path.join(ROOT,'docs','guide','img',l)])
    sys.exit(0)
import os,sys
from playwright.sync_api import sync_playwright
repo,lang,out=sys.argv[1:4]; os.makedirs(out,exist_ok=True)
def clip(pg,name,sel=None,h=None):
    pg.screenshot(path=f'{out}/{name}.png')
with sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':390,'height':760},device_scale_factor=2); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.route('**/*.js',lambda r:r.abort())
    pg.goto('file://'+os.path.abspath(repo)+'/index.html'); pg.wait_for_function("typeof showStep==='function'")
    pg.evaluate("document.documentElement.classList.remove('awr-locked')"); pg.add_style_tag(content='#saveBadge,.save-badge{display:none !important}')
    if lang=='fr': pg.evaluate("QCRP_I18N.toggle()"); pg.wait_for_timeout(300)
    pg.evaluate("showStep(1); window.scrollTo(0,0)"); pg.wait_for_timeout(200); clip(pg,'step1')
    def elshot(name, js):
        pg.evaluate("document.querySelectorAll('[data-shot]').forEach(e=>e.removeAttribute('data-shot'))")
        pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p=='fixed'||p=='sticky') e.style.visibility='hidden'})")
        ok=pg.evaluate(js)
        if ok: pg.locator('[data-shot]').first.screenshot(path=f'{out}/{name}.png')
        else: print('no element for',name)
        pg.evaluate("document.querySelectorAll('*').forEach(e=>{if(e.style.visibility=='hidden') e.style.visibility=''})")
    # (statement fold is described in text, no screenshot)
    #elshot('statement', "()=>{const d=[...document.querySelectorAll('.question-step.active details')].find(x=>/statement|relev/i.test((x.querySelector('summary')||{}).textContent||'')); if(!d) return false; d.open=true; d.setAttribute('data-shot','1'); return true}")
    elshot('aishortcut', "()=>{const d=[...document.querySelectorAll('.question-step.active details')].find(x=>/AI chat|chat IA|IA/i.test((x.querySelector('summary')||{}).textContent||'')); if(!d) return false; d.open=true; d.setAttribute('data-shot','1'); return true}")
    pg.evaluate("showStep(2); window.scrollTo(0,0)"); pg.wait_for_timeout(200); clip(pg,'step2')
    pg.evaluate("showStep(2)")
    elshot('step2gov', "()=>{const l=[...document.querySelectorAll('.question-step.active label')].find(x=>/When to start|Quand d|Quand c/i.test(x.textContent)); const d=l&&l.closest('.asset-row'); if(!d) return false; d.classList.remove('collapsed'); d.setAttribute('data-shot','1'); return true}")
    pg.evaluate("showStep(3); window.scrollTo(0,0)"); pg.wait_for_timeout(200); clip(pg,'step3')
    pg.evaluate("calculateRetirementPlan()"); pg.wait_for_timeout(800); pg.evaluate("window.scrollTo(0,0)"); clip(pg,'results')
    # Monte Carlo run box + Judge toggle (then back to the flat model so later shots are unchanged)
    pg.evaluate("document.getElementById('returnModel').value='montecarlo'; document.getElementById('mcRepeatable').checked=true; mcRerunN=0; mcSeedShift=0; calculateRetirementPlan()"); pg.wait_for_timeout(1200)
    elshot('mcrun', "()=>{const e=document.getElementById('mcRunBanner'); if(!e||!e.innerText.trim()) return false; e.setAttribute('data-shot','1'); e.scrollIntoView({block:'center'}); return true}")
    pg.evaluate("document.getElementById('returnModel').value='flat'; calculateRetirementPlan()"); pg.wait_for_timeout(600); pg.evaluate("window.scrollTo(0,0)")
    pg.evaluate("document.querySelectorAll('.year-cards details.yp').forEach(d=>d.open=false)")
    idx=pg.evaluate("(()=>{const l=[...document.querySelectorAll('.year-cards details.yp')]; let k=l.findIndex(d=>/held back|holds back|withh|retenue/i.test(d.textContent)); return k<0?1:k})()")
    pg.evaluate("i=>{const d=document.querySelectorAll('.year-cards details.yp')[i]; d.open=true; d.scrollIntoView();}", idx); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if((p=='fixed'||p=='sticky')) e.style.visibility='hidden'})"); pg.locator('.year-cards details.yp').nth(idx).screenshot(path=f'{out}/yearcard.png'); pg.evaluate("document.querySelectorAll('*').forEach(e=>{if(e.style.visibility=='hidden') e.style.visibility=''})")
    # menu
    pg.evaluate("showStep(1); window.scrollTo(0,0)"); pg.evaluate('toggleMenu(true)'); pg.wait_for_timeout(250)
    pg.wait_for_timeout(200); clip(pg,'menu'); pg.evaluate("closeMenu()")
    # couple
    pg.evaluate("showStep(1)"); pg.select_option('#calcMode','couple'); pg.fill('#hhNameMe','Alex'); pg.fill('#hhNameSp','Sam'); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(200); clip(pg,'couple')
    pg.evaluate("document.getElementById('currentRrsp').value = 400000; document.getElementById('currentTfsa').value = 60000; document.getElementById('spendAmount').value = 6000")
    pg.evaluate("calculateRetirementPlan()"); pg.evaluate("closeInfo()")
    pg.evaluate("document.getElementById('currentAge').value = 52; document.getElementById('currentRrsp').value = 50000; document.getElementById('currentTfsa').value = 20000")
    pg.evaluate("hhSwitch('me')"); pg.evaluate("calculateRetirementPlan()"); pg.wait_for_timeout(1200)
    pg.evaluate("document.getElementById('hhTabs').scrollIntoView()"); pg.evaluate("window.scrollBy(0,-20)"); clip(pg,'household')
    # expense sheet in couple mode
    pg.evaluate("showStep(2); openExpenses()")
    pg.evaluate("expDraft.items=[{name:'Mortgage',amount:'2500',freq:'monthly',pct:'60'},{name:'Property tax',amount:'3600',freq:'yearly',pct:''},{name:'Groceries',amount:'180',freq:'weekly',pct:'50'}]; expRender()")
    pg.wait_for_timeout(200); pg.evaluate("document.querySelector('#expSheet .sh').scrollTop=0"); clip(pg,'expenses_top')
    pg.evaluate("document.querySelector('#expList').scrollIntoView({block:'start'})"); pg.evaluate("document.querySelector('#expSheet .sh').scrollTop += -40"); pg.wait_for_timeout(100); clip(pg,'expenses_rows')
    pg.evaluate("expCancel()")
    pg.evaluate("showStep(7)"); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(200); clip(pg,'events')
    print(errs[:3]); br.close()
