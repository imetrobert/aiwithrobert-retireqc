#!/usr/bin/env python3
"""Builds guide.pdf = docs/guide-base.pdf (the original guide) + a "What is new" section.
To add a new feature to the guide: edit the SECTIONS text below, then run: python3 scripts/build_guide_update.py
(needs: pip install reportlab pypdf --break-system-packages). Do not edit guide.pdf by hand."""
import os, sys, io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP = 'qc' if os.path.exists(os.path.join(ROOT, 'CNAME')) and 'retireqc' in open(os.path.join(ROOT, 'CNAME')).read() else 'on'
FD = '/usr/share/fonts/truetype/liberation/'
pdfmetrics.registerFont(TTFont('B', FD + 'LiberationSans-Regular.ttf')); pdfmetrics.registerFont(TTFont('BB', FD + 'LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('BI', FD + 'LiberationSans-Italic.ttf')); pdfmetrics.registerFont(TTFont('BBI', FD + 'LiberationSans-BoldItalic.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('B', normal='B', bold='BB', italic='BI', boldItalic='BBI')
NAVY = colors.HexColor('#0b2a6b'); RED = colors.HexColor('#c8102e'); LIGHT = colors.HexColor('#eef3fb'); GREY = colors.HexColor('#475569')
S = {
 'eye': ParagraphStyle('eye', fontName='BB', fontSize=8, textColor=RED, spaceAfter=2, leading=10),
 'h1': ParagraphStyle('h1', fontName='BB', fontSize=20, textColor=NAVY, leading=24, spaceAfter=4),
 'h2': ParagraphStyle('h2', fontName='BB', fontSize=11.5, textColor=NAVY, leading=14, spaceBefore=9, spaceAfter=3),
 'p': ParagraphStyle('p', fontName='B', fontSize=9.3, leading=12.8, spaceAfter=4),
 'li': ParagraphStyle('li', fontName='B', fontSize=9.3, leading=12.6),
 'box': ParagraphStyle('box', fontName='B', fontSize=9, leading=12.2, textColor=colors.HexColor('#1e293b')),
}
def bullets(items): return ListFlowable([ListItem(Paragraph(t, S['li']), leftIndent=12, value='•') for t in items], bulletType='bullet', bulletFontSize=8, leftIndent=12, bulletColor=NAVY, spaceAfter=4)
def box(title, text):
    t = Table([[Paragraph('<b>%s</b><br/>%s' % (title, text), S['box'])]], colWidths=[6.4 * inch])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT), ('LINEBEFORE', (0, 0), (0, -1), 3, NAVY), ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    return [Spacer(1, 3), t, Spacer(1, 5)]
QC = APP == 'qc'
# ---------------------------------------------------------------- TEXT (English)
def en():
    gov = ('Retraite Québec Statement of Participation (your QPP estimate) and the public-sector pension statement' if QC else 'Service Canada CPP Statement of Contributions')
    what = 'the QPP estimate' if QC else 'the CPP estimate at 65'
    surv = 'QPP/CPP survivor benefits' if QC else 'CPP survivor benefits'
    return {
     'name': 'Quebec Retirement Planner' if QC else 'Ontario Retirement Planner',
     'eye': 'UPDATE · 22 NOVEMBER 2026', 'title': 'What is new in the planner',
     'intro': 'This section was added after the guide above was written. Where it differs from the pages above, <b>this section is the newer information</b>.',
     'blocks': [
      ('h2', 'Signing in, and two ways to save your scenarios'),
      ('p', 'The planner now asks you to sign in. The calculations still run on your own phone or computer: your figures are not sent anywhere while you plan. You can keep your scenarios in two ways (Menu):'),
      ('b', ['<b>Save on this device.</b> Copies stay in this browser on this device. You can reopen them any time here, but clearing your browser data erases them.',
             '<b>Save in the cloud</b> (My plans). Your plan is encrypted on your device with your <b>passphrase</b> before it is saved to your account, so you can open it on any device. Only your passphrase can open it, and it <b>cannot be recovered if you forget it</b>.']),
      ('p', 'Signing out asks whether to keep or clear the copies saved on this device. Keeping them is the default.'),
      ('h2', 'Planning as a couple'),
      ('p', 'In Step 1, the first question is <b>just you, or you and a spouse</b>. With a spouse, fill in the same form once for each person using the <b>Filling in</b> buttons at the top. Spending, inflation and returns are household settings: enter them once, in your own form.'),
      ('b', ['The <b>Household</b> tab merges both plans year by year, with one more tab for each person.',
             'Household spending is split between you automatically by income, or by a percentage you type, or by <b>who pays what</b> in the expense list (below).',
             '<b>Pension income splitting</b> is on by default: each year, up to 50% of the higher earner\'s eligible pension income is moved to the other spouse for tax and OAS clawback purposes, only when this lowers your combined tax. You can turn it off with the checkbox on the Household tab.',
             '<b>Spousal rollover</b> is on by default: the plan that ends first is treated as the first death (each person has their own "Plan until age"). Savings pass tax-free to the survivor, who covers 75% of the household spending (you can set 40% to 100%).']),
      ('box', 'Not modeled', surv + ' and survivor benefits from an employer pension are not included. Check them with your plan administrator.'),
      ('h2', 'The expense list'),
      ('p', 'Under the spending question in Step 2 (or Menu, Expenses), you can build your spending from a list instead of typing one number. List <b>regular recurring</b> expenses only; one-time or specific-year costs belong in Life events. Amounts are in today\'s money and are raised for inflation each year.'),
      ('b', ['Each row has its own frequency: <b>Monthly, Weekly or Yearly</b> (the default is Monthly). Enter the amount as you are billed.',
             '<b>Set all rows to</b> changes every row at once; you can then change any single row. <b>Show the total per</b> chooses the unit used for your spending target, which can also be set to Yearly.',
             'When you use the list, the spending fields are filled in and locked. Edit the list to change them, or choose <b>Stop using the list</b>.']),
      ('h2', 'Who pays what'),
      ('b', ['<b>Living with others, planning just for you:</b> each expense has two linked boxes, <b>You</b> and <b>Spouse / others</b>. Change one and the other adjusts so they always add up to 100%. Blank means you pay 100%. Only your share goes into your plan. There is also a box to set every row at once.',
             '<b>Couple mode:</b> the same two boxes show each person\'s share. Leave both blank to use the automatic split. The spouse\'s tab has a link to the same shared list. <b>Recommend an optimized split</b> tries different splits and picks the one that does best on tax and on how long the money lasts.']),
      ('h2', 'Life events'),
      ('p', 'Each life event (one-time or yearly) has the same two linked boxes. When you live with others and plan just for yourself, only your share is counted. In couple mode, <b>Recommend an optimized split of these events</b> chooses one percentage for all events on the form you have open and shows the estimated tax saved compared with your current split.'),
      ('h2', 'Withholding tax wording'),
      ('p', 'When a withdrawal has tax withheld at source, the yearly card says the bank withholds an amount, which will automatically be used to pay part of the tax you owe for the year, and shows what you receive in pocket. When nothing is withheld, it tells you there is no withholding tax, so you should put that money aside to pay your tax bill.'),
      ('h2', 'Reading your pension statements'),
      ('p', 'In Step 1, the optional statement shortcut can read a digital PDF of your %s on your own device, nothing is uploaded. It shows a <b>Preview</b> first, and only fills in %s after you tap <b>Apply</b>. Scans and screenshots are not read: you can always pick the number yourself.' % (gov, what)),
      ('h2', 'Menu changes'),
      ('b', ['<b>Expenses</b> now sits just under Life events.',
             'Saving is shown as two clear rows: <b>Save on this device</b> and <b>Save in the cloud</b>.',
             'The floating "My plans" button was removed so it no longer covers other buttons.']),
     ]}
# ---------------------------------------------------------------- TEXT (French, Quebec only)
def fr():
    return {
     'name': 'Planificateur de retraite du Québec',
     'eye': 'MISE À JOUR · 22 NOVEMBRE 2026', 'title': 'Nouveautés du planificateur',
     'intro': 'Cette section a été ajoutée après la rédaction du guide ci-dessus. Lorsqu\'elle diffère des pages précédentes, <b>cette section contient l\'information la plus récente</b>.',
     'blocks': [
      ('h2', 'Connexion et deux façons d\'enregistrer vos scénarios'),
      ('p', 'Le planificateur vous demande maintenant de vous connecter. Les calculs se font toujours sur votre téléphone ou votre ordinateur : vos chiffres ne sont envoyés nulle part pendant que vous planifiez. Vous pouvez conserver vos scénarios de deux façons (Menu) :'),
      ('b', ['<b>Enregistrer sur cet appareil.</b> Les copies restent dans ce navigateur, sur cet appareil. Vous pouvez les rouvrir en tout temps ici, mais effacer les données du navigateur les supprime.',
             '<b>Enregistrer dans le nuage</b> (Mes plans). Votre plan est chiffré sur votre appareil avec votre <b>phrase secrète</b> avant d\'être enregistré dans votre compte; vous pouvez donc l\'ouvrir sur tout appareil. Seule votre phrase secrète peut l\'ouvrir, et elle <b>ne peut pas être récupérée si vous l\'oubliez</b>.']),
      ('p', 'À la déconnexion, on vous demande de conserver ou d\'effacer les copies enregistrées sur cet appareil. Les conserver est le choix par défaut.'),
      ('h2', 'Planifier en couple'),
      ('p', 'À l\'étape 1, la première question est <b>vous seul(e), ou vous et un(e) conjoint(e)</b>. Avec un(e) conjoint(e), remplissez le même formulaire une fois pour chaque personne avec les boutons <b>Vous remplissez</b> en haut. Les dépenses, l\'inflation et les rendements sont des réglages du ménage : entrez-les une seule fois, dans votre propre formulaire.'),
      ('b', ['L\'onglet <b>Ménage</b> fusionne les deux plans année par année, avec un onglet de plus pour chaque personne.',
             'Les dépenses du ménage sont partagées automatiquement selon le revenu, ou selon un pourcentage que vous inscrivez, ou selon <b>qui paie quoi</b> dans la liste de dépenses (ci-dessous).',
             'Le <b>fractionnement du revenu de pension</b> est activé par défaut : chaque année, jusqu\'à 50 % du revenu de pension admissible de la personne au revenu le plus élevé est transféré à l\'autre conjoint(e) pour l\'impôt et la récupération de la PSV, seulement si cela réduit l\'impôt combiné. Vous pouvez le désactiver avec la case de l\'onglet Ménage.',
             'Le <b>transfert au conjoint survivant</b> est activé par défaut : le plan qui se termine en premier représente le premier décès (chaque personne a son propre « Espérance de vie visée »). Les épargnes passent sans impôt au survivant, qui assume 75 % des dépenses du ménage (réglable de 40 % à 100 %).']),
      ('box', 'Non modélisé', 'Les prestations de survivant du RRQ/RPC et d\'un régime de retraite d\'employeur ne sont pas incluses. Vérifiez-les auprès de l\'administrateur de votre régime.'),
      ('h2', 'La liste de dépenses'),
      ('p', 'Sous la question sur les dépenses à l\'étape 2 (ou Menu, Dépenses), vous pouvez bâtir vos dépenses à partir d\'une liste au lieu d\'inscrire un seul chiffre. Inscrivez seulement les dépenses <b>régulières et récurrentes</b>; les coûts ponctuels ou propres à une année vont dans les Événements de vie. Les montants sont en dollars d\'aujourd\'hui et sont indexés chaque année.'),
      ('b', ['Chaque ligne a sa propre fréquence : <b>Mensuelle, Hebdomadaire ou Annuelle</b> (Mensuelle par défaut). Entrez le montant tel que facturé.',
             '<b>Mettre toutes les lignes à</b> change toutes les lignes d\'un coup; vous pouvez ensuite modifier une seule ligne. <b>Afficher le total par</b> choisit l\'unité de votre cible de dépenses, qui peut aussi être annuelle.',
             'Quand vous utilisez la liste, les champs de dépenses sont remplis et verrouillés. Modifiez la liste pour les changer, ou choisissez <b>Ne plus utiliser la liste</b>.']),
      ('h2', 'Qui paie quoi'),
      ('b', ['<b>Vous vivez avec d\'autres personnes et planifiez seulement pour vous :</b> chaque dépense a deux cases liées, <b>Vous</b> et <b>Conjoint(e) / autres</b>. Modifiez l\'une et l\'autre s\'ajuste pour que le total soit toujours 100 %. Vide : vous payez 100 %. Seule votre part entre dans votre plan. Une case permet aussi d\'appliquer un pourcentage à toutes les lignes.',
             '<b>Mode couple :</b> les deux mêmes cases montrent la part de chaque personne. Laissez les deux vides pour utiliser le partage automatique. L\'onglet du/de la conjoint(e) donne accès à la même liste partagée. <b>Recommander un partage optimisé</b> essaie différents partages et retient celui qui donne les meilleurs résultats pour l\'impôt et la durée de l\'épargne.']),
      ('h2', 'Événements de vie'),
      ('p', 'Chaque événement de vie (ponctuel ou annuel) a les deux mêmes cases liées. Si vous vivez avec d\'autres personnes et planifiez seulement pour vous, seule votre part est comptée. En mode couple, <b>Recommander un partage optimisé de ces événements</b> choisit un pourcentage pour tous les événements du formulaire ouvert et montre l\'impôt estimé économisé par rapport à votre partage actuel.'),
      ('h2', 'Formulation de la retenue d\'impôt'),
      ('p', 'Quand un retrait comporte une retenue d\'impôt à la source, la carte annuelle indique que la banque retient un montant, qui servira automatiquement à payer une partie de l\'impôt dû pour l\'année, et montre ce que vous recevez en main. Quand rien n\'est retenu, elle indique qu\'il n\'y a pas de retenue d\'impôt et qu\'il faut mettre cet argent de côté pour payer votre facture d\'impôt.'),
      ('h2', 'Lire vos relevés de pension'),
      ('p', 'À l\'étape 1, le raccourci facultatif pour les relevés peut lire un PDF numérique de votre relevé de participation de Retraite Québec (votre estimation de la rente du RRQ) ou de votre relevé de pension du secteur public, sur votre propre appareil; rien n\'est téléversé. Un <b>aperçu</b> s\'affiche d\'abord, et les champs ne sont remplis qu\'après avoir touché <b>Appliquer</b>. Les numérisations et captures d\'écran ne sont pas lues : vous pouvez toujours choisir le chiffre vous-même.'),
      ('h2', 'Changements au menu'),
      ('b', ['<b>Dépenses</b> se trouve maintenant juste sous Événements de vie.',
             'L\'enregistrement est présenté en deux lignes claires : <b>Enregistrer sur cet appareil</b> et <b>Enregistrer dans le nuage</b>.',
             'Le bouton flottant « Mes plans » a été retiré pour ne plus cacher d\'autres boutons.']),
     ]}
def story(t, first_page_label):
    out = [Paragraph(t['eye'], S['eye']), Paragraph(t['title'], S['h1'])]
    rule = Table([['']], colWidths=[6.9 * inch], rowHeights=[3]); rule.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 2, NAVY), ('LINEBELOW', (0, 0), (-1, 0), 1.2, RED)])); out += [rule, Spacer(1, 6), Paragraph(t['intro'], S['p'])]
    for b in t['blocks']:
        k = b[0]
        if k == 'h2': out.append(Paragraph(b[1], S['h2']))
        elif k == 'p': out.append(Paragraph(b[1], S['p']))
        elif k == 'b': out.append(bullets(b[1]))
        elif k == 'box': out += box(b[1], b[2])
    return out
def render(t, start_page):
    buf = io.BytesIO(); label = t['name'] + ' · ' + ('User guide' if t['name'].startswith(('Quebec', 'Ontario')) else 'Guide de l\'utilisateur')
    def foot(c, d):
        c.saveState(); c.setFont('B', 7); c.setFillColor(GREY); c.drawCentredString(letter[0] / 2, 30, '%s · %d' % (label, start_page + d.page - 1)); c.restoreState()
    doc = BaseDocTemplate(buf, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch)
    doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')], onPage=foot)])
    doc.build(story(t, start_page)); buf.seek(0); return PdfReader(buf)
def main():
    base = os.path.join(ROOT, 'docs', 'guide-base.pdf')
    if not os.path.exists(base): sys.exit('docs/guide-base.pdf is missing (it is the original guide).')
    w = PdfWriter(); br = PdfReader(base)
    for p in br.pages: w.add_page(p)
    n = len(br.pages)
    for t in ([en(), fr()] if QC else [en()]):
        r = render(t, n + 1)
        for p in r.pages: w.add_page(p)
        n += len(r.pages)
    w.add_metadata({k: v for k, v in (br.metadata or {}).items() if isinstance(v, str)})
    with open(os.path.join(ROOT, 'guide.pdf'), 'wb') as f: w.write(f)
    print('guide.pdf written: %d pages' % n)
if __name__ == '__main__': main()
