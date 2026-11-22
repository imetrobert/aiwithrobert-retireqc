#!/usr/bin/env python3
"""Builds guide.pdf from the text files in docs/guide/ (en.md, and fr.md when the planner is bilingual) and the
screenshots in docs/guide/img/<lang>/. To change the guide: edit the .md file(s), commit; the "Build guide"
workflow rebuilds guide.pdf. Locally: pip install reportlab pillow --break-system-packages; python3 scripts/build_guide.py
Markup: see docs/guide/README.md."""
import os, re, sys, glob
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak,
                                NextPageTemplate, Image, KeepTogether, ListFlowable, ListItem)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GD = os.path.join(ROOT, 'docs', 'guide')
def _font():
    for d in ('/usr/share/fonts/truetype/liberation/', '/usr/share/fonts/liberation/', '/usr/share/fonts/truetype/liberation2/'):
        if os.path.exists(d + 'LiberationSans-Regular.ttf'): return d
    sys.exit('Liberation Sans font not found (sudo apt-get install fonts-liberation).')
FD = _font()
for n, f in (('B', 'Regular'), ('BB', 'Bold'), ('BI', 'Italic'), ('BBI', 'BoldItalic')): pdfmetrics.registerFont(TTFont(n, FD + 'LiberationSans-%s.ttf' % f))
registerFontFamily('B', normal='B', bold='BB', italic='BI', boldItalic='BBI')
NAVY = colors.HexColor('#0b2a6b'); ACCENT = colors.HexColor('#c8102e'); LIGHT = colors.HexColor('#eef3fb'); GREY = colors.HexColor('#475569'); LINE = colors.HexColor('#cbd5e1')
ST = {
 'eye': ParagraphStyle('eye', fontName='BB', fontSize=7.5, textColor=ACCENT, leading=10, spaceAfter=2),
 'h1': ParagraphStyle('h1', fontName='BB', fontSize=19, textColor=NAVY, leading=23, spaceAfter=3),
 'h2': ParagraphStyle('h2', fontName='BB', fontSize=11, textColor=NAVY, leading=14, spaceBefore=8, spaceAfter=2),
 'p': ParagraphStyle('p', fontName='B', fontSize=9.2, leading=12.6, spaceAfter=4),
 'li': ParagraphStyle('li', fontName='B', fontSize=9.2, leading=12.4),
 'cell': ParagraphStyle('cell', fontName='B', fontSize=8.6, leading=11),
 'cellh': ParagraphStyle('cellh', fontName='BB', fontSize=8.6, leading=11, textColor=colors.white),
 'box': ParagraphStyle('box', fontName='B', fontSize=8.8, leading=12, textColor=colors.HexColor('#1e293b')),
 'toc': ParagraphStyle('toc', fontName='B', fontSize=10.5, leading=15),
 'cov1': ParagraphStyle('cov1', fontName='BB', fontSize=30, textColor=colors.white, leading=34, spaceAfter=8),
 'cov2': ParagraphStyle('cov2', fontName='B', fontSize=14, textColor=colors.white, leading=18, spaceAfter=4),
 'cov3': ParagraphStyle('cov3', fontName='B', fontSize=10, textColor=colors.HexColor('#cbd5e1'), leading=13, spaceAfter=3),
}
def inline(t):
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t); t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    return t
def parse(path):
    txt = open(path, encoding='utf-8').read().replace('\r', '')
    meta = {}; m = re.match(r'---\n(.*?)\n---\n', txt, re.S)
    if m:
        for ln in m.group(1).split('\n'):
            if ':' in ln: k, v = ln.split(':', 1); meta[k.strip()] = v.strip()
        txt = txt[m.end():]
    pages = []; cur = None
    for ln in txt.split('\n'):
        if ln.startswith('# '): cur = {'title': ln[2:].strip(), 'eyebrow': '', 'side': [], 'lines': []}; pages.append(cur); continue
        if cur is None: continue
        mm = re.match(r'(eyebrow|side):\s*(.*)$', ln)
        if mm and not cur['lines']:
            if mm.group(1) == 'eyebrow': cur['eyebrow'] = mm.group(2).strip()
            else: cur['side'] = [x.strip() for x in mm.group(2).split(',') if x.strip()]
            continue
        cur['lines'].append(ln)
    return meta, pages
def blocks(lines, lang, content_w):
    out = []; i = 0
    def img(fn, w):
        p = os.path.join(GD, 'img', lang, fn)
        if not os.path.exists(p): sys.exit('missing screenshot: ' + p)
        from PIL import Image as PI
        iw, ih = PI.open(p).size; im = Image(p, width=w, height=w * ih / iw)
        t = Table([[im]], colWidths=[w + 4]); t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, LINE), ('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 1), ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)])); return t
    while i < len(lines):
        ln = lines[i]
        if not ln.strip(): i += 1; continue
        if ln.startswith('## '): out.append(Paragraph(inline(ln[3:]), ST['h2'])); i += 1; continue
        m = re.match(r'!\[[^\]]*\]\(([^)]+)\)(?:\{w=([\d.]+)\})?', ln.strip())
        if m: out.append(img(m.group(1), float(m.group(2) or 2.4) * inch)); out.append(Spacer(1, 4)); i += 1; continue
        if ln.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('>'): buf.append(lines[i][1:].strip()); i += 1
            title = ''; 
            if buf and re.fullmatch(r'\*\*.+\*\*', buf[0]): title = '<b>%s</b><br/>' % inline(buf[0][2:-2]); buf = buf[1:]
            t = Table([[Paragraph(title + inline(' '.join(buf)), ST['box'])]], colWidths=[content_w])
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT), ('LINEBEFORE', (0, 0), (0, -1), 3, NAVY), ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
            out += [Spacer(1, 2), t, Spacer(1, 5)]; continue
        if ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.fullmatch(r'\|[\s:|-]+\|?', lines[i].strip()): rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            n = len(rows[0]); cw = [content_w * 0.28, content_w * 0.72] if n == 2 else [content_w / n] * n
            data = [[Paragraph(inline(c), ST['cellh'] if r == 0 else ST['cell']) for c in row] for r, row in enumerate(rows)]
            t = Table(data, colWidths=cw, repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3), ('LEFTPADDING', (0, 0), (-1, -1), 5)]))
            out += [t, Spacer(1, 5)]; continue
        if re.match(r'- ', ln):
            items = []
            while i < len(lines) and (lines[i].startswith('- ') or (lines[i].startswith('  ') and items and lines[i].strip())):
                if lines[i].startswith('- '): items.append(lines[i][2:].strip())
                else: items[-1] += ' ' + lines[i].strip()
                i += 1
            out.append(ListFlowable([ListItem(Paragraph(inline(t), ST['li']), leftIndent=12, value='•') for t in items], bulletType='bullet', bulletFontSize=8, leftIndent=12, bulletColor=NAVY, spaceAfter=4)); continue
        if re.match(r'\d+\. ', ln):
            items = []
            while i < len(lines) and (re.match(r'\d+\. ', lines[i]) or (lines[i].startswith('   ') and items and lines[i].strip())):
                if re.match(r'\d+\. ', lines[i]): items.append(re.sub(r'^\d+\. ', '', lines[i]).strip())
                else: items[-1] += ' ' + lines[i].strip()
                i += 1
            out.append(ListFlowable([ListItem(Paragraph(inline(t), ST['li']), leftIndent=16) for t in items], bulletType='1', bulletFontName='BB', bulletFontSize=8.5, bulletColor=NAVY, leftIndent=16, spaceAfter=4)); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r'(## |> |\||- |\d+\. |!\[)', lines[i]): buf.append(lines[i].strip()); i += 1
        out.append(Paragraph(inline(' '.join(buf)), ST['p']))
    return out
class Doc(BaseDocTemplate):
    def __init__(self, fn, footer, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.65 * inch, bottomMargin=0.7 * inch, **kw)
        self.footer = footer; self.found = {}
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='f')
        cv = Frame(0.9 * inch, 1.2 * inch, letter[0] - 1.8 * inch, letter[1] - 2.8 * inch, id='c')
        self.addPageTemplates([PageTemplate(id='cover', frames=[cv], onPage=self.cover_bg), PageTemplate(id='body', frames=[fr], onPage=self.foot)])
    def cover_bg(self, c, d):
        c.saveState(); c.setFillColor(NAVY); c.rect(0, 0, letter[0], letter[1], stroke=0, fill=1); c.setFillColor(ACCENT); c.rect(0, 0, letter[0], 10, stroke=0, fill=1); c.restoreState()
    def foot(self, c, d):
        c.saveState(); c.setFont('B', 7); c.setFillColor(GREY); c.drawCentredString(letter[0] / 2, 30, '%s · %d' % (self.footer, d.page)); c.restoreState()
    def afterFlowable(self, f):
        k = getattr(f, '_pagekey', None)
        if k: self.found[k] = self.page
class KP(Paragraph):
    pass
def build(pdf_path):
    files = [f for f in ('en.md', 'fr.md') if os.path.exists(os.path.join(GD, f))]
    if not files: sys.exit('docs/guide/en.md not found')
    langs = [(f[:-3],) + parse(os.path.join(GD, f)) for f in files]
    first_meta = langs[0][1]
    footer = '%s · %s' % (first_meta.get('app', ''), first_meta.get('doc', 'User guide')) if len(langs) == 1 else '%s · %s' % (first_meta.get('app', ''), langs[1][1].get('app', ''))
    def story(found):
        s = []
        # cover
        s.append(Spacer(1, 40))
        for lang, meta, pages in langs:
            s.append(Paragraph(inline(meta['app']), ST['cov1']) if lang == langs[0][0] else Spacer(1, 18))
            if lang != langs[0][0]: s.append(Paragraph(inline(meta['app']), ParagraphStyle('c1b', parent=ST['cov2'], fontName='BB', fontSize=20, leading=24)))
            s.append(Paragraph(inline(meta['doc']), ST['cov2'])); s.append(Paragraph(inline(meta.get('tagline', '')), ST['cov3']))
        if len(langs) > 1: s += [Spacer(1, 14), Paragraph(inline(first_meta.get('both', '')), ST['cov3'])]
        s.append(Spacer(1, 150))
        for lang, meta, pages in langs: s.append(Paragraph(inline(meta.get('notice', '')), ST['cov3']))
        s += [NextPageTemplate('body'), PageBreak()]
        n = 0
        for lang, meta, pages in langs:
            cw = letter[0] - 1.6 * inch
            if len(langs) > 1 or True:
                s.append(Paragraph(inline(meta.get('lang_label', '')), ST['eye'])); s.append(Paragraph(inline(meta.get('toc', 'What is in this guide')), ST['h1']))
                rows = []
                for k, p in enumerate(pages, 1): rows.append([Paragraph('%d' % k, ST['toc']), Paragraph(inline(p['title']), ST['toc']), Paragraph('%s' % found.get((lang, k), ''), ST['toc'])])
                t = Table(rows, colWidths=[0.4 * inch, cw - 1.1 * inch, 0.6 * inch]); t.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('ALIGN', (2, 0), (2, -1), 'RIGHT'), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4), ('TEXTCOLOR', (0, 0), (0, -1), NAVY)]))
                s += [t, PageBreak()]
            for k, p in enumerate(pages, 1):
                head = []
                e = Paragraph(inline(p['eyebrow']), ST['eye']) if p['eyebrow'] else Spacer(1, 0)
                h = Paragraph(inline(p['title']), ST['h1']); h._pagekey = (lang, k)
                rule = Table([['']], colWidths=[cw], rowHeights=[3]); rule.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 2, NAVY), ('LINEBELOW', (0, 0), (-1, 0), 1, ACCENT)]))
                head = [e, h, rule, Spacer(1, 5)]
                if p['side']:
                    lw = 4.15 * inch; body = blocks(p['lines'], lang, lw - 6)
                    side = []
                    from PIL import Image as PI
                    hs = []
                    for fn in p['side']:
                        iw, ih = PI.open(os.path.join(GD, 'img', lang, fn)).size; hs.append(ih / iw)
                    avail = 7.6 - 0.25 * len(hs)          # inches of height for all side images on one page
                    w_in = max(1.3, min(2.45, avail / sum(hs)))
                    for fn in p['side']:
                        side += blocks(['![](%s){w=%.2f}' % (fn, w_in)], lang, 2.4 * inch)
                    t = Table([[body, side]], colWidths=[lw, cw - lw], splitInRow=1); t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (0, 0), 10), ('RIGHTPADDING', (1, 0), (1, 0), 0), ('TOPPADDING', (0, 0), (-1, -1), 0)]))
                    s += head + [t]
                else: s += head + blocks(p['lines'], lang, cw)
                s.append(PageBreak())
        if isinstance(s[-1], PageBreak): s.pop()
        return s
    found = {}
    for _ in range(2):
        d = Doc(pdf_path, footer, title='%s · %s' % (first_meta.get('app', ''), first_meta.get('doc', '')), author='AI with Robert')
        d.build(story(found)); found = dict(d.found)
    return found
if __name__ == '__main__':
    out = os.path.join(ROOT, 'guide.pdf'); f = build(out)
    from pypdf import PdfReader
    print('guide.pdf written: %d pages' % len(PdfReader(out).pages))
