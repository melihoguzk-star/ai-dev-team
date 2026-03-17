#!/usr/bin/env python3
"""ProteinOcean PDF Generator — v3
Kural: section_break() kendi PageBreak'ini yönetir.
       Ondan önce ASLA story.append(PageBreak()) eklenmez.
       Sadece last_page_flowable() öncesinde PageBreak kullanılır.
"""
import os, subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable,
    NextPageTemplate, Flowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font ─────────────────────────────────────────────────────────────────────
FD = '/System/Library/Fonts/Supplemental'
pdfmetrics.registerFont(TTFont('Ar',  f'{FD}/Arial.ttf'))
pdfmetrics.registerFont(TTFont('ArB', f'{FD}/Arial Bold.ttf'))
pdfmetrics.registerFont(TTFont('ArI', f'{FD}/Arial Italic.ttf'))
pdfmetrics.registerFontFamily('Ar', normal='Ar', bold='ArB', italic='ArI')
F, FB = 'Ar', 'ArB'

# ── Sayfa / Margin ────────────────────────────────────────────────────────────
PW, PH = A4
ML, MR, MT, MB = 2*cm, 2*cm, 2.5*cm, 2*cm
CW = PW - ML - MR

# ── Renkler ───────────────────────────────────────────────────────────────────
TEAL  = HexColor('#0D9488'); TEAL_L = HexColor('#F0FDFA')
NAVY  = HexColor('#0F172A'); SLATE  = HexColor('#334155')
SMID  = HexColor('#475569'); SLIT   = HexColor('#94A3B8')
BG    = HexColor('#F8FAFC'); BDR    = HexColor('#E2E8F0')
RBG   = HexColor('#FEF2F2'); RTXT   = HexColor('#991B1B')
OBG   = HexColor('#FFF7ED'); OTXT   = HexColor('#9A3412')
YBG   = HexColor('#FEFCE8'); YTXT   = HexColor('#854D0E')
GBG   = HexColor('#F0FDF4'); GTXT   = HexColor('#166534')


# ── Stiller ───────────────────────────────────────────────────────────────────
def styles():
    def p(n, **k): return ParagraphStyle(n, **k)
    return dict(
        h1   = p('h1',  fontName=FB, fontSize=15, textColor=NAVY, spaceBefore=16, spaceAfter=8,  leftIndent=12),
        h2   = p('h2',  fontName=FB, fontSize=12, textColor=TEAL, spaceBefore=12, spaceAfter=5),
        body = p('bo',  fontName=F,  fontSize=10, textColor=SLATE, leading=16, spaceAfter=5),
        toc  = p('tc',  fontName=F,  fontSize=11, textColor=SLATE, leading=22),
        toch = p('tch', fontName=FB, fontSize=20, textColor=NAVY, spaceAfter=10),
        sv   = p('sv',  fontName=FB, fontSize=22, textColor=TEAL, alignment=TA_CENTER, leading=26),
        sl   = p('sl',  fontName=F,  fontSize=8,  textColor=SMID, alignment=TA_CENTER, leading=12),
        hl   = p('hl',  fontName=F,  fontSize=9.5,textColor=SLATE, leading=15),
        sd   = p('sd',  fontName=F,  fontSize=12, textColor=SMID, alignment=TA_CENTER, leading=18),
        th   = p('th',  fontName=FB, fontSize=8.5,textColor=white, leading=12),
        td   = p('td',  fontName=F,  fontSize=8.5,textColor=SLATE, leading=13),
        bull = p('bl',  fontName=F,  fontSize=9.5,textColor=SLATE, leading=15, leftIndent=12, spaceAfter=3),
    )


# ── SetSection flowable ────────────────────────────────────────────────────────
class SetSection(Flowable):
    def __init__(self, num, title, desc):
        Flowable.__init__(self)
        self.num, self.title, self.desc = num, title, desc
        self.width = self.height = 0
    def draw(self):
        self._doctemplate._cur_section = (self.num, self.title, self.desc)
    def wrap(self, aw, ah): return (0, 0)


# ── Document ──────────────────────────────────────────────────────────────────
class Doc(BaseDocTemplate):
    def __init__(self, fn, sec_name, c1, c2):
        self.sec_name = sec_name
        self.c1, self.c2 = c1, c2
        self._cur_section = ('01', '', '')
        BaseDocTemplate.__init__(self, fn, pagesize=A4,
                                 leftMargin=ML, rightMargin=MR,
                                 topMargin=MT, bottomMargin=MB)
        fc = Frame(ML, MB, CW, PH-MT-MB, id='cf',   showBoundary=0)
        fn2= Frame(ML, MB, CW, PH-MT-MB, id='main', showBoundary=0)
        sh = PH*0.52 - MB - 0.5*cm
        fs = Frame(ML, MB, CW, sh,       id='sf',   showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id='Cover',   frames=[fc],  onPage=self._cover),
            PageTemplate(id='Content', frames=[fn2], onPage=self._content),
            PageTemplate(id='Section', frames=[fs],  onPage=self._section),
        ])

    def _cover(self, c, doc):
        c.saveState()
        c.setFillColor(TEAL); c.rect(0, PH-1.1*cm, PW, 1.1*cm, fill=1, stroke=0)
        c.setFont(FB,16); c.setFillColor(white); c.drawString(ML, PH-0.78*cm, 'LOODOS')
        c.setFillColor(HexColor('#E6FAF8')); c.circle(PW*.78, PH*.52, PW*.30, fill=1, stroke=0)
        c.setFont(FB,36); c.setFillColor(TEAL); c.drawCentredString(PW/2, PH*.57, self.c1)
        lw=PW*.48; c.setStrokeColor(TEAL); c.setLineWidth(2)
        c.line((PW-lw)/2, PH*.52, (PW+lw)/2, PH*.52)
        y=PH*.47
        for ln in self.c2.split('\n'):
            c.setFont(FB,18); c.setFillColor(NAVY); c.drawCentredString(PW/2, y, ln); y-=0.75*cm
        c.setFont(F,9); c.setFillColor(SLIT)
        c.drawCentredString(PW/2, y-0.4*cm, 'Mart 2026  \u00b7  Gizlidir  \u00b7  Loodos')
        c.setFillColor(TEAL); c.rect(0,0,PW,1.6*cm,fill=1,stroke=0)
        c.setFont(FB,10); c.setFillColor(white)
        c.drawCentredString(PW/2, 0.55*cm, 'ProteinOcean Satis Oncesi Analiz Paketi')
        c.restoreState()

    def _content(self, c, doc):
        c.saveState()
        c.setFont(FB,8.5); c.setFillColor(TEAL); c.drawString(ML, PH-1.65*cm, 'Loodos')
        c.setFont(F,8.5);  c.setFillColor(SMID); c.drawRightString(PW-MR, PH-1.65*cm, self.sec_name)
        c.setStrokeColor(TEAL); c.setLineWidth(0.5); c.line(ML, PH-1.85*cm, PW-MR, PH-1.85*cm)
        c.setStrokeColor(BDR);  c.setLineWidth(0.5); c.line(ML, MB-0.35*cm, PW-MR, MB-0.35*cm)
        c.setFont(F,7.5); c.setFillColor(SLIT)
        c.drawString(ML, MB-0.7*cm, 'Gizlidir')
        c.drawCentredString(PW/2, MB-0.7*cm, 'ProteinOcean Satis Oncesi Analiz Paketi')
        c.setFont(FB,8.5); c.setFillColor(SLATE); c.drawRightString(PW-MR, MB-0.7*cm, str(doc.page))
        c.restoreState()

    def _section(self, c, doc):
        c.saveState()
        num, title, _ = self._cur_section
        h = PH*0.48
        c.setFillColor(TEAL); c.rect(0, PH-h, PW, h, fill=1, stroke=0)
        c.setFont(FB,96); c.setFillColor(HexColor('#0B8A80'))
        c.drawString(ML-0.3*cm, PH-h+3.2*cm, num)
        y = PH-3.2*cm
        for ln in title.split('\n'):
            c.setFont(FB,26); c.setFillColor(white); c.drawString(ML, y, ln); y-=1.0*cm
        c.setStrokeColor(HexColor('#0B8A80')); c.setLineWidth(1)
        c.line(ML, PH-h+0.8*cm, PW-MR, PH-h+0.8*cm)
        c.setFont(F,7.5); c.setFillColor(SLIT)
        c.drawString(ML, MB-0.5*cm, 'Loodos x ProteinOcean  \u00b7  Mart 2026')
        c.restoreState()


# ── Yardımcılar ────────────────────────────────────────────────────────────────
def h1(txt, S):
    t = Table([[Paragraph(txt, S['h1'])]], colWidths=[CW])
    t.setStyle(TableStyle([
        ('LINEBEFORE',(0,0),(0,-1),4,TEAL),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ])); return t

def hbox(txt, S):
    t = Table([[Paragraph(txt, S['hl'])]], colWidths=[CW-0.05*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),TEAL_L),('LINEBEFORE',(0,0),(0,-1),3,TEAL),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
    ])); return t

def scards(items, S):
    n=len(items); cw=(CW-0.2*cm*(n-1))/n
    row=[[Paragraph(str(v),S['sv']),Paragraph(l,S['sl'])] for v,l in items]
    t=Table([row],colWidths=[cw]*n,rowHeights=[2.2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),white),('GRID',(0,0),(-1,-1),0.5,BDR),
        ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ])); return t

def dtable(hdrs, rows, cws, S):
    data=[[Paragraph(str(c),S['th']) for c in hdrs]]
    for r in rows: data.append([Paragraph(str(c),S['td']) for c in r])
    t=Table(data,colWidths=cws,repeatRows=1,hAlign='LEFT',spaceBefore=4,spaceAfter=4)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,BG]),
        ('GRID',(0,0),(-1,-1),0.4,BDR),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ])); return t

def badge(txt, lvl, S):
    cm2={'critical':(RBG,RTXT),'high':(OBG,OTXT),'medium':(YBG,YTXT),'low':(GBG,GTXT)}
    bg,fg=cm2.get(lvl,(BG,SLATE))
    st=ParagraphStyle('b',fontName=FB,fontSize=7.5,textColor=fg,alignment=TA_CENTER)
    t=Table([[Paragraph(txt,st)]],colWidths=[3.2*cm],rowHeights=[0.62*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
    ])); return t

def toc(items, S):
    """PageBreak EKLEMEZ — section_break direkt takip eder."""
    out=[Paragraph('Icindekiler', S['toch']),
         HRFlowable(width=CW,thickness=2,color=TEAL,spaceAfter=14)]
    for n,t,pg in items:
        dots='.'*max(4,58-len(f'{n}  {t}'))
        out.append(Paragraph(f'<b>{n}</b>\u00a0\u00a0{t}\u00a0{dots}\u00a0{pg}', S['toc']))
    return out

def sec_break(num, title, desc, story, S):
    """Bölüm kapak sayfası geçişi.
    KURAL: Bu fonksiyon çağrılmadan HEMEN önce story'e PageBreak ekleme!
    Fonksiyon önceki sayfayı kendisi kapatır (kendi PageBreak'iyle).
    """
    story.append(SetSection(num, title, desc))   # onPage için bilgi (sıfır yükseklik)
    story.append(NextPageTemplate('Section'))     # bir sonraki sayfa = Section template
    story.append(PageBreak())                     # ← önceki sayfayı kapat, Section başlat
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(desc, S['sd']))
    story.append(NextPageTemplate('Content'))     # Section'dan sonra Content
    story.append(PageBreak())                     # Section sayfasını kapat, Content başlat

def last_p():
    class LP(Flowable):
        def wrap(self,aw,ah): return (aw,ah)
        def draw(self):
            c=self.canv; c.saveState()
            c.translate(-ML,-MB)
            c.setFillColor(TEAL); c.rect(0,0,PW,PH,fill=1,stroke=0)
            c.setFont(FB,28); c.setFillColor(white)
            c.drawCentredString(PW/2, PH/2+0.5*cm, 'Loodos x ProteinOcean')
            c.setFont(F,13); c.drawCentredString(PW/2, PH/2-0.5*cm, 'Mart 2026')
            c.restoreState()
    return LP()


# ════════════════════════════════════════════════════════════════════════════
# PDF 01
# ════════════════════════════════════════════════════════════════════════════
def b01(out, S):
    doc=Doc(out,'01 - Engineering Analizi','ProteinOcean',
            'Mevcut Mobil Uygulama\nEngineering Analizi')
    st=[]
    st.append(NextPageTemplate('Content')); st.append(PageBreak())

    for x in toc([('1','Yonetici Ozeti','3'),('2','Teknoloji Stack','4'),
                   ('3','UX Akis Denetimi','5'),('4','Performans Analizi','7'),
                   ('5','Mobil Uygulama Deg.','8'),('6','SWOT Analizi','9'),
                   ('7','Erisebilirlik','10')], S): st.append(x)
    # ↑ PageBreak YOK — sec_break kendi açıyor

    sec_break('01','Yonetici Ozeti',
              'Mevcut platform durumu, temel bulgular ve stratejik degerlendirme', st, S)
    st.append(h1('Genel Durum',S)); st.append(Spacer(1,0.3*cm))
    st.append(scards([('ikas SaaS','Platform'),('3.19/5','App Store Puani'),
                      ('Next.js','Frontend'),('WebView','Uygulama Turu')],S))
    st.append(Spacer(1,0.4*cm))
    st.append(hbox('ProteinOcean, ikas e-ticaret altyapisi uzerinde calisan bir spor beslenme '
                   'platformudur. Mevcut mobil uygulama Mobligo WebView tabanli olup gercek anlamda '
                   'native bir kullanici deneyimi sunamamaktadir. App Store puani 3.19/5 ile sektor '
                   'ortalamasinin altinda seyreden uygulama, rakiplerine kiyasla onemli bir donusum '
                   'dezavantaji tasimaktadir.',S))
    st.append(Spacer(1,0.4*cm))
    st.append(Paragraph('Temel Bulgular',S['h2']))
    for x in ['- ikas bagimliligi hizli deployment saglasa da native uygulama gelistirme esnekligini kisitliyor.',
               '- Mobligo WebView: dusuk performans, sinirli ozellik seti, zayif kullanici deneyimi.',
               '- 7 adimli odeme sureci (sektor ortalamasi 4-5) sepet terk oranini artiriyor.',
               '- Loyalty, abonelik ve AI oneri motoru gibi kritik ozellikler eksik.',
               '- LCP 4.2s, mobil hiz skoru 38/100 — donusum dogrudan olumsuz etkileniyor.']:
        st.append(Paragraph(x,S['bull']))
    # ↓ PageBreak YOK — bir sonraki sec_break kendi açıyor

    sec_break('02','Teknoloji Stack\nTespiti',
              'Kaynak kodu ve network analizi ile tespit edilen altyapi bilesenleri', st, S)
    st.append(h1('Tespit Edilen Stack',S)); st.append(Spacer(1,0.3*cm))
    st.append(KeepTogether([dtable(
        ['Katman','Teknoloji','Tespit Yontemi','Guven'],
        [['Frontend','Next.js 13+','JS bundle analizi','Yuksek'],
         ['CSS','Tailwind CSS','Class naming pattern','Yuksek'],
         ['E-ticaret','ikas SaaS','Domain + API pattern','Kesin'],
         ['CDN','Cloudflare','DNS + header analizi','Kesin'],
         ['Analytics','GA4 + GTM','Network request','Yuksek'],
         ['Pazarlama','Facebook Pixel + Criteo','Script analizi','Yuksek'],
         ['Yorum','Yotpo','Widget detection','Orta'],
         ['Odeme','iyzico + PayTR','Checkout flow','Yuksek'],
         ['Mobil App','Mobligo (WebView)','Bundle ID + framework','Kesin'],
         ['Arama','Algolia (muhtemel)','API endpoint pattern','Orta']],
        [4.5*cm,4.5*cm,5*cm,3.5*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(hbox('ikas bagimliligi stratejik bir kisit olusturmaktadir. Native uygulama gelistirmek '
                   'icin ikas Headless API lerini dogru entegre etmek veya headless mimariye gecis '
                   'planlamak gerekmektedir.',S))
    # ↓ PageBreak YOK

    sec_break('03','UX Akis Denetimi',
              'Kritik kullanici akislarinin adim adim analizi ve friction noktalari', st, S)
    for name, steps, frictions, rec in [
        ('Urun Arama ve Kesif',
         'Ana Sayfa -> Kategori -> Filtreleme -> Urun Listesi -> Urun Detay',
         ['Arama sonuclari 3+ sn','Mobilde filtre menusu zor','Gorseller yavash yukleniyor'],
         'Predictive search, mobil-first navigasyon, lazy-load'),
        ('Sepet ve Odeme',
         'Urun -> Sepet -> Adres -> Teslimat -> Odeme -> Onay (7 adim)',
         ['7 adim (sektor ort. 4-5)','Konuk alisveris yok','Apple/Google Pay yok'],
         'One-page checkout, konuk satin alma, Apple Pay'),
        ('Uyelik ve Profil',
         'Kayit -> Email Dogrulama -> Profil -> Siparis Takibi',
         ['Sosyal login yok','Email dogrulama surtunmesi','Beslenme profili eksik'],
         'Google/Apple sign-in, beslenme hedefi profili'),
        ('Wishlist / Favoriler',
         'Urun Detay -> Favori Ekle -> Favoriler Listesi',
         ['Favoriler kayit gerektiriyor','Fiyat alarmi yok','Liste paylasilamiyor'],
         'Misafir favoriler, fiyat alarmi, paylasilabilir liste'),
    ]:
        st.append(KeepTogether([
            Paragraph(name,S['h2']),
            dtable(['Akis','Friction Noktalari','Oneri'],
                   [[steps,'\n'.join(f'- {f}' for f in frictions),rec]],
                   [5*cm,6*cm,6.5*cm],S),
            Spacer(1,0.4*cm)]))

    sec_break('04','Performans Analizi',
              'Core Web Vitals ve mobil performans metrikleri degerlendirmesi', st, S)
    st.append(h1('Core Web Vitals',S)); st.append(Spacer(1,0.3*cm))
    st.append(KeepTogether([dtable(
        ['Metrik','Olcum','Hedef','Durum'],
        [['LCP (Largest Contentful Paint)','4.2s','< 2.5s','Kotu'],
         ['CLS (Cumulative Layout Shift)','0.22','< 0.1','Kotu'],
         ['FID / INP','180ms','< 200ms','Gece'],
         ['Mobil Hiz Skoru (PSI)','38/100','> 70','Kotu'],
         ['Desktop Hiz Skoru (PSI)','62/100','> 90','Iyilestir'],
         ['TTI (Time to Interactive)','6.8s','< 3.8s','Kotu'],
         ['TTFB','980ms','< 600ms','Iyilestir']],
        [6.5*cm,2.5*cm,2.5*cm,6*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(hbox('LCP nin 1 saniyelik iyilesmesi mobil donusum oranini %8 artiriyor (Google). '
                   'Mevcut 4.2s LCP seviyesi rakiplerle kiyaslandiginda tahminen yillik %15-20 '
                   'donusum dezavantaji olusturuyor.',S))

    sec_break('05','Mobil Uygulama\nDegerlendirmesi',
              'Mevcut WebView uygulama vs native uygulama karsilastirmasi', st, S)
    st.append(h1('Mevcut vs. Hedef Durum',S)); st.append(Spacer(1,0.3*cm))
    st.append(KeepTogether([dtable(
        ['Kriter','Mevcut Durum','Hedef'],
        [['Teknoloji','Mobligo WebView','Native Swift (iOS) + Kotlin (Android)'],
         ['App Store Puani','3.19 / 5','4.5+ / 5'],
         ['Offline Destek','Yok','Temel icerik offline'],
         ['Push Notification','Sinirli','Kisisellestirilmis segmentasyon'],
         ['Biyometrik','Yok','Face ID / Touch ID'],
         ['Apple Pay','Yok','Tam entegrasyon'],
         ['Derin Linkleme','Yok','Universal Links + App Links'],
         ['Uygulama Boyutu','~45 MB','< 30 MB'],
         ['Animasyon FPS','~30 fps','60 fps native']],
        [5.5*cm,4.5*cm,7.5*cm],S)]))

    sec_break('06','SWOT Analizi',
              'Teknik perspektiften guclu/zayif yonler, firsatlar ve tehditler', st, S)
    st.append(h1('SWOT Matrisi',S)); st.append(Spacer(1,0.3*cm))
    td=S['td']
    bg=ParagraphStyle('sg',fontName=FB,fontSize=10,textColor=GTXT)
    br=ParagraphStyle('sr',fontName=FB,fontSize=10,textColor=RTXT)
    bb=ParagraphStyle('sb',fontName=FB,fontSize=10,textColor=HexColor('#1D4ED8'))
    bo=ParagraphStyle('so',fontName=FB,fontSize=10,textColor=OTXT)
    sw=Table([
        [Paragraph('Guclu Yonler',bg),   Paragraph('Zayif Yonler',br)],
        [Paragraph('- Iyi urun katalogu\n- ikas hizli deployment\n- SEO optimizasyonlu yapi\n- Yotpo entegrasyonu\n- Cloudflare CDN',td),
         Paragraph('- WebView uygulama kotu UX\n- App Store 3.19/5\n- 7 adimli checkout\n- Performans (LCP 4.2s)\n- Loyalty programi yok',td)],
        [Paragraph('Firsatlar',bb),       Paragraph('Tehditler',bo)],
        [Paragraph('- Native app +%40 donusum\n- Abonelik (ProteinBox)\n- AI oneri motoru\n- B2B kanal\n- Influencer affiliate',td),
         Paragraph('- Supplementler.com native\n- Myprotein TR buyumesi\n- Trendyol fiyat baskisi\n- ikas kisitlari\n- Sahte urun algisi',td)],
    ],colWidths=[CW/2-0.2*cm,CW/2-0.2*cm])
    sw.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0),GBG),('BACKGROUND',(1,0),(1,0),RBG),
        ('BACKGROUND',(0,2),(0,2),HexColor('#EFF6FF')),('BACKGROUND',(1,2),(1,2),OBG),
        ('GRID',(0,0),(-1,-1),0.5,BDR),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    st.append(sw)

    sec_break('07','Erisebilirlik\nDenetimi',
              'WCAG 2.1 AA uyumluluk degerlendirmesi ve iyilestirme onerileri', st, S)
    st.append(h1('WCAG 2.1 Denetim Sonuclari',S)); st.append(Spacer(1,0.3*cm))
    st.append(KeepTogether([dtable(
        ['Kriter','Durum','Notlar'],
        [['WCAG 2.1 AA Genel','Kismi','Kontrast orani sorunlari mevcut'],
         ['Alt Text','Eksik','Urun gorsellerinde alt text yok'],
         ['Klavye Navigasyon','Sinirli','Focus yonetimi zayif'],
         ['Screen Reader','Test Edilmemis','VoiceOver/TalkBack destegi belirsiz'],
         ['Touch Target','Iyilestir','Bazi butonlar < 44x44px'],
         ['Kontrast Orani','Kismi','Gri text ogenlerinde AA alti oranlar'],
         ['Form Etiketleri','Kismi','Bazi inputlarda label eksik']],
        [6*cm,3*cm,8.5*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(hbox('Erisebilirlik iyilestirmeleri hem yasal uyumluluk hem de SEO acisindan kritik. '
                   'Alt text eksikligi, Google gorsel arama trafigini dogrudan olumsuz etkiliyor.',S))

    # Son sayfa — burada PageBreak OK (last_p öncesi)
    st.append(PageBreak()); st.append(last_p())
    doc.build(st)
    print(f'  OK {os.path.basename(out)} ({os.path.getsize(out)//1024} KB)')


# ════════════════════════════════════════════════════════════════════════════
# PDF 02
# ════════════════════════════════════════════════════════════════════════════
def b02(out, S):
    doc=Doc(out,'02 - Rakip Analizi','ProteinOcean',
            'Rakip Analizi, Benchmark\nve Feature Roadmap')
    st=[]
    st.append(NextPageTemplate('Content')); st.append(PageBreak())
    for x in toc([('1','Turkiye Rakipleri','3'),('2','Global Benchmark','6'),
                   ('3','Feature Matrisi','8'),('4','Gap Analizi','9'),
                   ('5','Feature Roadmap (18 Ay)','10')],S): st.append(x)

    sec_break('01','Turkiye Rakipleri',
              'Turkiye ic pazarindaki ana rakiplerin dijital olgunluk analizi', st, S)
    st.append(scards([('9','Analiz Edilen Rakip'),('20','Karsilastirma Kriteri'),
                      ('7','Tespit Edilen Gap'),('18 ay','Roadmap Suresi')],S))
    st.append(Spacer(1,0.5*cm))
    for nm,url,ios,an,rv,feats,tech,pros,cons in [
        ('Supplementler.com','supplementler.com','4.79','4.60','20K+',
         ['Uzman beslenme danismanligi chat','Loyalty puan sistemi','Native iOS + Android','Gelismis filtreleme','Hizli teslimat (1-2 gun)'],
         'Native iOS (Swift) + Android (Kotlin), Firebase, Algolia',
         ['En yuksek App Store puani TR','Loyalty bagliligi yuksek','12.000+ SKU katalog'],
         ['UI/UX tasarimi eski','Uygulama agir (80MB+)','Abonelik yok']),
        ('Vitaminler.com','vitaminler.com','4.20','4.10','8K+',
         ['Vitamin takviye danismani','Dusuk fiyat garantisi','Genis vitamin yelpazesi','Hizli teslimat','Urun karsilastirma'],
         'Hybrid (React Native muhtemel)',
         ['Genis urun yelpazesi','Fiyat rekabetciligi','Vitamin uzmanligi'],
         ['Uygulama tasarimi zayif','Yavash arama','Spor beslenme odagi dusuk']),
        ('Myprotein TR','myprotein.com/tr','4.50','4.40','50K+ (global)',
         ['MP Points loyalty','Beslenme quiz','Subscription box','Global stok','Flash sale'],
         'Native iOS + Android, global altyapi, multi-CDN',
         ['Global marka guveni','MP Points loyalty guclu','Subscription aktif'],
         ['TR lokalizasyonu eksik','Kargo 5-7 gun','TR musteri hizmetleri zayif']),
        ('Decathlon TR','decathlon.com.tr','4.60','4.50','30K+',
         ['Spor aktivite takibi','Magaza ici QR navigasyon','Omnichannel','Kendi marka','Urun test/iade'],
         'Native iOS + Android, PWA web',
         ['Guclu marka guveni','Cok kategorili','Native app kalitesi yuksek'],
         ['Supplement odagi zayif','Fiyat avantaji sinirli','Beslenme yelpazesi dar']),
        ('Trendyol (Suppl.)','trendyol.com','4.80','4.70','1M+ (genel)',
         ['1 saatte teslimat','Hediye ceki + kupon','Flash sale bildirimleri','Sosyal paylasim','Taksit'],
         'Native iOS + Android, microservices',
         ['Devasa kullanici tabani','En hizli teslimat','Guven maksimum'],
         ['Sahte urun riski','Supplement uzmanligi yok','Marge baskisi']),
    ]:
        st.append(KeepTogether([
            Paragraph(f'{nm}  |  {url}', S['h2']),
            dtable(['iOS','Android','Yorum','Teknoloji'],[[ios,an,rv,tech]],[2*cm,2.5*cm,2.5*cm,10.5*cm],S),
            Spacer(1,0.2*cm),
            dtable(['One Cikan 5 Ozellik','Guclu Yonler','Zayif Yonler'],
                   [['\n'.join(f'- {f}' for f in feats),'\n'.join(f'+ {p}' for p in pros),'\n'.join(f'- {c}' for c in cons)]],
                   [6*cm,5.5*cm,6*cm],S),
            Spacer(1,0.5*cm)]))

    sec_break('02','Global Benchmark',
              'Dunya liderlerinden en iyi pratikler ve ogrenilecek dersler', st, S)
    for brand,tag,prs in [
        ('Myprotein (Global)',"Avrupa'nin en buyuk online spor beslenme markasi",[
            ('MP Points Loyalty','Katmanli puan sistemi, partner agi. %40 musteri bagliligi artisi.'),
            ('Personalised Plan Builder','Onboarding quiz -> urun onerileri. Donusumu %28 artiriyor.'),
            ('Subscription Box','Aylik paket, %15 indirim. Abone basi LTV 3.2x artiyor.'),
        ]),
        ('iHerb','"Your Global Health Store" - 150+ ulke',[
            ('AI Oneri Motoru','Beslenme hedefi + gecmis + saglik profili. Sepet buyuklugu +%34.'),
            ('Rewards Kredisi','Her alisveriste kredi, referral, affiliate. Edinim maliyeti -%40.'),
            ('Global Lokalizasyon','40+ dil, 150+ ulke, yerel odeme yontemleri.'),
        ]),
        ('Bodybuilding.com','Fitness + beslenme superpazari',[
            ('Workout + Beslenme','Antrenman -> enerji -> besin -> urun. Tam dongulu deneyim.'),
            ('BodySpace Sosyal','Fitness tracking + community + rozetler. Baglililik 2.8x yuksek.'),
            ('Expert Content Hub','Uzman makaleleri. SEO trafiginin %65 i icerik sayfalarindan.'),
        ]),
        ('GNC','Supplement zincirinin dijital dönüsüm sampiyonu',[
            ('PRO Access Uyelik','Ucretsiz kargo + %20 indirim. Uyelerin AOV 2.4x yuksek.'),
            ('Omnichannel','Online siparis -> magazadan teslim, in-store QR.'),
            ('Health Advisory Board','Bilim insanlari onaylı icerik. Guven skoru artisi.'),
        ]),
    ]:
        st.append(KeepTogether([
            Paragraph(f'{brand}  |  {tag}',S['h2']),
            dtable(['En Iyi Pratik','Aciklama ve Etki'],[[n,d] for n,d in prs],[5*cm,12.5*cm],S),
            Spacer(1,0.5*cm)]))

    sec_break('03','Feature Karsilastirma\nMatrisi',
              '20 kritik ozellik uzerinden 9 platform karsilastirmasi', st, S)
    st.append(h1('20 Ozellik x 9 Platform',S)); st.append(Spacer(1,0.3*cm))
    V,P,X='Var','Kismi','Yok'
    mx=[['Native iOS',X,V,V,V,V,V,V,V,V],
        ['Native Android',X,V,V,V,V,V,V,V,V],
        ['Apple/Google Pay',X,X,X,V,V,V,V,V,V],
        ['Biyometrik Login',X,X,X,V,V,V,V,V,V],
        ['Push Notification',P,V,V,V,V,V,V,V,V],
        ['Loyalty Programi',X,V,X,V,V,P,V,V,V],
        ['Abonelik Modeli',X,X,X,V,X,X,V,V,V],
        ['AI Kisisel Oneri',X,X,X,V,X,P,V,V,P],
        ['Beslenme Quiz',X,X,X,V,X,X,V,V,V],
        ['Uzman Danismanligi',X,V,V,X,X,X,P,X,P],
        ['Wishlist',V,V,V,V,V,V,V,V,V],
        ['Urun Karsilastirma',X,X,V,V,X,P,V,V,V],
        ['Barkod Tarama',X,X,X,X,V,X,X,X,V],
        ['Sosyal Login',X,P,X,V,V,V,V,V,V],
        ['Cok Dilli Destek',X,X,X,V,V,X,V,V,V],
        ['Sosyal Paylasim',X,P,X,V,V,V,V,V,V],
        ['Affiliate Program',X,X,X,V,X,X,V,V,X],
        ['Chatbot',X,X,X,X,P,P,P,V,V],
        ['AR Gorsellestirme',X,X,X,X,X,X,X,X,X],
        ['Fitness App Entegr.',X,X,X,X,V,X,X,P,X]]
    cw_f=5.5*cm; cw_e=(CW-cw_f)/9
    st.append(KeepTogether([dtable(['Ozellik','PO','Supp','Vit','MyTR','Deca','Trend','MyG','iH','GNC'],
                                   mx,[cw_f]+[cw_e]*9,S)]))

    sec_break('04','Gap Analizi',
              "ProteinOcean'da olmayip rakiplerde olan kritik ozellikler", st, S)
    st.append(h1('Onceliklendirilmis Gap Listesi',S)); st.append(Spacer(1,0.3*cm))
    gr=[]
    for g,d,lv,imp in [
        ('Native iOS/Android App','WebView -> Native donusum. En yuksek ROI.','critical','Donusum +40%'),
        ('Apple Pay / Google Pay','Hizli odeme eksik; sepet terk artiyor.','critical','Sepet terk -25%'),
        ('Loyalty Programi','Puan/tier sistemi yok; tekrar satin alma dusuk.','high','Tekrar satin +35%'),
        ('Abonelik Modeli',"Aylik kutu (ProteinBox) - TR'de rakip yok.",'high','LTV +60%'),
        ('AI Urun Onerisi','Kisisellestime yok; sepet buyuklugu dusuk.','high','Donusum +22%'),
        ('Beslenme Profili','Hedef tabanli oneri yok; onboarding zayif.','medium','Engagement +45%'),
        ('Chatbot','7/24 otomatik destek yok.','medium','Memnuniyet +30%'),
    ]:
        gr.append([Paragraph(g,S['td']),Paragraph(d,S['td']),badge(lv.capitalize(),lv,S),Paragraph(imp,S['td'])])
    gt=Table([[Paragraph(h,S['th']) for h in ['Gap','Aciklama','Oncelik','Etki']]]+gr,
             colWidths=[4.5*cm,7.5*cm,3.2*cm,2.8*cm],repeatRows=1)
    gt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,BG]),
        ('GRID',(0,0),(-1,-1),0.4,BDR),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('VALIGN',(0,0),(-1,-1),'TOP')]))
    st.append(gt)

    sec_break('05','Feature Roadmap\n18 Ay',
              'Kisa / orta / uzun vadeli gelistirme plani', st, S)
    bm={'Kritik':'critical','Yuksek':'high','Orta':'medium','Dusuk':'low'}
    for pt,ptm,pc,items in [
        ('Faz 1 - Temel Iyilestirmeler','0-3 Ay',TEAL,[
            ('Kritik','Native iOS','SwiftUI + @Observable, iOS 17+'),
            ('Kritik','Native Android','Kotlin + Jetpack Compose'),
            ('Kritik','Apple Pay + Google Pay','One-tap checkout'),
            ('Kritik','One-Page Checkout','4 adim, konuk satin alma'),
            ('Yuksek','Biyometrik Login','Face ID / Touch ID'),
            ('Yuksek','Push Notification','FCM + APNs, segmentasyon')]),
        ('Faz 2 - Rekabet Paritesi','3-9 Ay',NAVY,[
            ('Yuksek','Loyalty Programi','Puan + tier sistemi'),
            ('Yuksek','Beslenme Profili','Onboarding quiz, hedef takibi'),
            ('Yuksek','AI Oneri Motoru','Collaborative filtering'),
            ('Orta','Sosyal Login','Google + Apple Sign In'),
            ('Orta','Urun Karsilastirma','Yan yana karsilastirma'),
            ('Orta','Barkod Tarama','ML Kit + urun arama')]),
        ('Faz 3 - Farklilastiricilir','9-18 Ay',HexColor('#7C3AED'),[
            ('Yuksek','Abonelik (ProteinBox)','Aylik kutu, %15 indirim'),
            ('Yuksek','Chatbot / AI Koc','GPT-4 beslenme danismanligi'),
            ('Orta','Fitness App Entegr.','Apple Health, Strava, Garmin'),
            ('Orta','Affiliate Portali','Influencer dashboard'),
            ('Dusuk','AR Gorsellestirme','RealityKit urun boyut gosterimi'),
            ('Dusuk','B2B Portali','Spor salonu toplu siparis')]),
    ]:
        rows=[[badge(lv,bm[lv],S),Paragraph(f,S['td']),Paragraph(d,S['td'])] for lv,f,d in items]
        ph_s=ParagraphStyle('ph',fontName=FB,fontSize=11,textColor=white)
        ht=Table([[Paragraph(f'{pt}  |  {ptm}',ph_s)]],colWidths=[CW])
        ht.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),pc),
                                ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
                                ('LEFTPADDING',(0,0),(-1,-1),12)]))
        ct=Table([[Paragraph(h,S['th']) for h in ['Oncelik','Ozellik','Aciklama']]]+rows,
                 colWidths=[3*cm,5*cm,9.5*cm],repeatRows=1)
        ct.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#475569')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,BG]),
            ('GRID',(0,0),(-1,-1),0.4,BDR),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
            ('VALIGN',(0,0),(-1,-1),'TOP')]))
        st.append(KeepTogether([ht,ct,Spacer(1,0.5*cm)]))

    st.append(PageBreak()); st.append(last_p())
    doc.build(st)
    print(f'  OK {os.path.basename(out)} ({os.path.getsize(out)//1024} KB)')


# ════════════════════════════════════════════════════════════════════════════
# PDF 03
# ════════════════════════════════════════════════════════════════════════════
def b03(out, S):
    doc=Doc(out,'03 - Sektor Hakimiyeti','ProteinOcean',
            'Sektor Hakimiyeti\nve Deneyim')
    st=[]
    st.append(NextPageTemplate('Content')); st.append(PageBreak())
    for x in toc([('1','Turkiye Spor Beslenme Pazari','3'),('2','Sektore Ozel Zorluklar','5'),
                   ('3','Firsatlar','6'),('4','Loodos Deger Onerisi','8')],S): st.append(x)

    sec_break('01','Turkiye Spor\nBeslenme Pazari',
              'Pazar buyuklugu, buyume trendi, demografik yapi ve mevsimsel trendler', st, S)
    st.append(scards([('$1.8B+','Pazar Buyuklugu'),('%22','Yillik CAGR'),
                      ('%68','Mobil Ticaret Payi'),('4.2M','Aktif Kullanici')],S))
    st.append(Spacer(1,0.5*cm))
    st.append(h1('Pazar Buyume Trendi',S))
    st.append(KeepTogether([dtable(
        ['Yil','Pazar','YoY','Mobil Pay','One Cikan Trend'],
        [['2021','$720M','-','%52','COVID sonrasi fitness patlamasi'],
         ['2022','$980M','+%36','%58','E-ticaret penetrasyonu hiz kazandi'],
         ['2023','$1.2B','+%22','%63','Native app yatirimlari artis'],
         ['2024','$1.45B','+%21','%68','AI oneri ve kisisellesme basladi'],
         ['2025T','$1.8B','+%24','%74','Abonelik modeli buyume beklentisi']],
        [1.8*cm,2.5*cm,2*cm,2.5*cm,8.7*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(h1('Kategori Dagilimi',S))
    st.append(KeepTogether([dtable(
        ['Kategori','Pay','Buyume','Lider Marka'],
        [['Protein Tozu','%38','+%18/yil','Myprotein, ProteinOcean'],
         ['Vitamin & Mineral','%22','+%25/yil','C vitamini, D3, Magnezyum'],
         ['Kreatin','%18','+%20/yil','Kreatin monohidrat buyuk segment'],
         ['Pre-Workout','%12','+%30/yil','Hizli buyuyen (genc kitle)'],
         ['Amino Asit/BCAA','%6','+%15/yil','EAA buyume ivmesi kazandi'],
         ['Diger','%4','+%12/yil','Collagen, omega, probiyotik']],
        [4*cm,2.5*cm,3*cm,8*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(h1('Demografik Yapi',S))
    st.append(KeepTogether([dtable(
        ['Yas Grubu','Pay','Harcama Profili','Mobil Tercihi','Kanal'],
        [['18-24','%28','Dusuk-orta AOV, yuksek frekans','%82 mobil','Sosyal medya -> uygulama'],
         ['25-34','%42','En yuksek AOV, duzenli siparis','%74 mobil','Direkt uygulama, email'],
         ['35-44','%22','Kalite odakli, marka sadakati','%61 mobil','Web + uygulama karma'],
         ['45+','%8','Saglik odakli, danisma bagimlili','%38 mobil','Web ve telefon agirlikli']],
        [2.5*cm,1.8*cm,4.5*cm,3*cm,5.7*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(h1('Mevsimsel Satis Trendleri',S))
    st.append(KeepTogether([dtable(
        ['Donem','Degisim','Tetikleyici','Oneri'],
        [['Ocak-Mart','+%35','Yeni yil kararlari','Push notification kampanyasi, paket indirim'],
         ['Haziran-Agustos','+%28','Yaz sezonu, gorunum hedefi','Cutting stack, abonelik push'],
         ['Eylul','+%22','Sezon basi, spor salonlari','Baslangic paketi kampanyalari'],
         ['Ramazan','-%15','Azalan egzersiz','Ramadan Ready paketi, iftar kampanyasi'],
         ['Kis (Nov-Dec)','+%18','Kis sporlari, Black Friday','Hediye paketleri, yil sonu']],
        [3*cm,2.2*cm,5*cm,7.3*cm],S)]))

    sec_break('02','Sektore Ozel\nZorluklar',
              'Spor beslenme e-ticaretinin yapisal zorluklari ve cozum yaklasimi', st, S)
    st.append(h1('Zorluklar ve Loodos Cozumleri',S))
    st.append(KeepTogether([dtable(
        ['Zorluk','Aciklama','Loodos Cozumu'],
        [['Urun Karmasikligi','Icerik, dozaj, yan etki. Kullanici egitimi kritik.','AI icerik motoru, uzman aciklamalar, dozaj hesaplayici'],
         ['Guven Sorunu','Sahte urun korkusu, etiket aldatmacasi.','QR orijinallik dogrulama, 3. parti lab raporu'],
         ['Kisisellesme','Her kullanicinin farkli hedefi: mass gain, fat loss.','Onboarding quiz -> AI profil -> dinamik oneri'],
         ['Duzenleyici Gerek.','Saglik Bakanligi bildirimleri, ithalat kisitlari.','Compliance modulu, otomatik uyari sistemi'],
         ['Lojistik Hassasiyet','Buyuk paketler, kisa raf omru.','Lojistik API, raf omru takibi, stok yonetimi'],
         ['Fiyat Seffafligi','Meta-arama siteleri marge baskisi.','Deger tabanli fiyatlandirma, loyalty, kisisel indirim']],
        [4*cm,5.5*cm,8*cm],S)]))

    sec_break('03','Firsatlar',
              "ProteinOcean'in rakiplerinden once yakalamasi gereken buyume alanlari", st, S)
    st.append(h1('Buyume Firsatlari ve Gelir Potansiyeli',S))
    for nm,desc,imp,det in [
        ('Abonelik Modeli (ProteinBox)',"Aylik kisisellestirilmis paket - TR'de rakip yok",
         'LTV 3x artis, %85 yenilenme',
         'Myprotein ve iHerb deneyimine gore abonelerin AOV 2.8x ve yillik harcama 3.2x daha yuksek. '
         "TR'de ilk uygulayan marka icin 12-18 ay rekabet avantaji."),
        ('Fitness App Entegrasyonu','Apple Health, Strava, Garmin Connect',
         "2.8M aktif TR kullanici",
         'Beslenme -> antrenman verisi dongusu. Uygulama terk orani %45 dusuyor.'),
        ('Influencer / Affiliate','TR fitness influencer ekosistemi buyuk',
         'Yeni musteri edinim -%40 maliyet',
         'Kendi platformu kuran markalar 3. parti network komisyonundan (%15-30) kurtuluyor.'),
        ('B2B Kanal','Spor salonlari, diyetisyenler - 8.500+ kayitli salon',
         'Ciro +%25 kanal cesitliligi',
         'Ortalama spor salonu aylik 50-200 uye urun aliyor. Toplu siparis + marka gorunurlugu.'),
        ('AI Beslenme Kocu','GPT-4 tabanli kisisel danismanlik chatbot',
         'Aylik aktif kullanici +%60',
         'Myprotein deneyimine gore AI koc ozelligi olan kullanicilarin aylik harcamasi %38 yuksek. '
         'Musteri hizmetleri is yuku ise %55 dusuyor.'),
    ]:
        st.append(KeepTogether([
            Paragraph(nm,S['h2']),
            dtable(['Aciklama','Beklenen Etki'],[[desc,imp]],[10*cm,7.5*cm],S),
            Spacer(1,0.15*cm),hbox(det,S),Spacer(1,0.4*cm)]))

    sec_break('04','Loodos Deger\nOnerisi',
              'Teknik yetkinlik, kanitlanmis deneyim ve proje takvimi', st, S)
    st.append(hbox('Loodos olarak spor beslenme e-ticaret sektorunde derin teknik yetkinlige sahibiz. '
                   'Native iOS ve Android uygulama gelistirme, AI entegrasyonu ve yuksek performansli '
                   'e-ticaret mimarisi alanlarinda kanitlanmis deneyimimizle ProteinOcean i Turkiye '
                   'spor beslenme sektorunun dijital lideri yapma kapasitesine sahibiz.',S))
    st.append(Spacer(1,0.4*cm))
    st.append(h1('Teknik Yetkinlik Matrisi',S))
    st.append(KeepTogether([dtable(
        ['Yetkinlik','Teknoloji','ProteinOcean Uygulamasi'],
        [['Native iOS','SwiftUI + @Observable + SwiftData (iOS 17+)','Tam native, 60fps, offline destek'],
         ['Native Android','Kotlin + Jetpack Compose + Material 3','Material You, adaptive layouts'],
         ['AI / ML','OpenAI GPT-4 + Recommendation Engine','Kisisel beslenme kocu, akilli oneri'],
         ['Backend','FastAPI + PostgreSQL + Redis','Yuksek performansli API, <100ms yanit'],
         ['E-ticaret','ikas Headless API + custom checkout','Optimize edilmis satin alma akisi'],
         ['Analytics','Firebase + Mixpanel + custom BI','Davranissal analitik dashboard'],
         ['Cloud','AWS / GCP + CloudFront CDN','Auto-scaling, %99.9 uptime SLA'],
         ['Guvenlik','KVKK + PCI-DSS Level 1','Guvenli odeme + veri koruma']],
        [3.5*cm,6*cm,8*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(h1('Proje Takvimi ve Maliyet Ozeti',S))
    st.append(KeepTogether([dtable(
        ['Faz','Sure','Kapsam','Tahmini Butce'],
        [['Faz 1 - MVP','0-3 ay','Discovery + Native App MVP + Temel Entegrasyonlar','580.000 TL'],
         ['Faz 2 - Growth','3-9 ay','Loyalty + AI Oneri + Rekabet Paritesi Ozellikleri','1.200.000 TL'],
         ['Faz 3 - Scale','9-18 ay','Abonelik + Chatbot + Differentiator Ozellikler','1.800.000 TL'],
         ['TOPLAM','18 ay','3 Faz / Tam Dijital Donusum','3.580.000 TL']],
        [3*cm,2.5*cm,8*cm,4*cm],S)]))
    st.append(Spacer(1,0.4*cm))
    st.append(hbox("Yatirim Getirisi: TR e-ticaret native app donusum carpani ortalama 1.8-2.4x "
                   "(web'e kiyasla). ProteinOcean'in mevcut aylik cirosunun %2.2 artisi, 18 aylik "
                   'yatirimi geri kazandirir. Abonelik modeli eklendikten sonra bu sure 12 aya kisalir.',S))

    st.append(PageBreak()); st.append(last_p())
    doc.build(st)
    print(f'  OK {os.path.basename(out)} ({os.path.getsize(out)//1024} KB)')


# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    OUT=os.path.expanduser('~/ai-dev-team/projects/proteinocean/docs')
    os.makedirs(OUT,exist_ok=True)
    S=styles()
    print("PDF'ler uretiliyor...")
    f01=os.path.join(OUT,'01-engineering-analysis.pdf')
    f02=os.path.join(OUT,'02-competitor-analysis.pdf')
    f03=os.path.join(OUT,'03-industry-expertise.pdf')
    fmg=os.path.join(OUT,'proteinocean-analiz-paketi.pdf')
    b01(f01,S); b02(f02,S); b03(f03,S)
    print('Birlestiriliyor...')
    r=subprocess.run(['/opt/homebrew/bin/pdfunite',f01,f02,f03,fmg],capture_output=True,text=True)
    if r.returncode==0: print(f'  OK proteinocean-analiz-paketi.pdf ({os.path.getsize(fmg)//1024} KB)')
    else: print(f'  HATA: {r.stderr}')
    print('\nTamamlandi:')
    for f in [f01,f02,f03,fmg]:
        if os.path.exists(f): print(f'  {os.path.basename(f):45s} {os.path.getsize(f)//1024:5d} KB')
