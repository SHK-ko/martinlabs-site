# 마틴랩스 홈페이지 빌드: src/*.html 본문 + 공통 머리말·푸터·폼 → site/
import json, pathlib, re

ROOT = pathlib.Path(__file__).parent
SRC, OUT = ROOT / 'src', ROOT / 'site'
BASE = 'https://martinlabs.kr'
GA_ID = ''  # GA4 측정 ID 발급 후 입력 (예: G-XXXXXXX)

ORG = {
  "@type": "Organization", "@id": BASE + "/#org",
  "name": "주식회사 마틴랩스", "alternateName": "Martin Labs", "url": BASE + "/",
  "description": "마틴랩스는 기업·기관·병원을 AX 컨설팅과 AI 마케팅으로 도와 업무혁신과 사업 성장을 만드는 전문 기업입니다.",
  "telephone": "+82-10-2788-2911", "email": "pdshk08@gmail.com", "taxID": "499-81-02639",
  "address": {"@type": "PostalAddress", "streetAddress": "목동동로12길 50 동성빌딩 4층 474호",
              "addressLocality": "양천구", "addressRegion": "서울특별시", "addressCountry": "KR"},
  "employee": {"@type": "Person", "@id": "https://seohuikyung.com/#person", "name": "서희경",
               "jobTitle": "대표이사", "url": "https://seohuikyung.com/"},
  "sameAs": ["https://seohuikyung.com/"]
}

NAV = [('/marketing/', '마케팅'), ('/ax/', 'AX 적용'), ('/consulting/', '컨설팅')]

def header(path):
    items = ''.join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if h == path else ""}>{t}</a></li>' for h, t in NAV)
    return f'''<a class="skip" href="#main">본문 바로가기</a>
<header class="site"><div class="wrap">
  <a class="logo" href="/">MARTIN <span>LABS</span></a>
  <button class="menu-btn" aria-label="메뉴 열기" aria-expanded="false" aria-controls="gnb">☰</button>
  <nav class="gnb" id="gnb" aria-label="주 메뉴"><ul>{items}
    <li><a class="btn sm" href="#contact" data-cta="header">상담 신청</a></li></ul></nav>
</div></header>'''

FOOTER = '''<footer class="site"><div class="wrap">
  <div class="cols">
    <div>
      <strong>주식회사 마틴랩스 (Martin Labs)</strong>
      <address>대표자 서희경 · 사업자등록번호 499-81-02639<br>
      서울특별시 양천구 목동동로12길 50 동성빌딩 4층 474호<br>
      전화 <a href="tel:010-2788-2911">010-2788-2911</a> · 이메일 <a href="mailto:pdshk08@gmail.com">pdshk08@gmail.com</a> / <a href="mailto:pd1shk@naver.com">pd1shk@naver.com</a></address>
    </div>
    <ul>
      <li><a href="/marketing/">GEO 마케팅</a></li>
      <li><a href="/ax/">AI 업무 적용 지원</a></li>
      <li><a href="/consulting/">AX 컨설팅</a></li>
      <li><a href="https://seohuikyung.com/">대표 서희경 소개</a></li>
      <li><a href="/privacy/"><strong>개인정보처리방침</strong></a></li>
    </ul>
  </div>
  <p class="copy">© 2026 Martin Labs. All rights reserved.</p>
</div></footer>
<a class="fab" href="#contact" data-cta="fab">무료 상담 신청</a>
__FLOAT__
<script src="/assets/site.js" defer></script>'''

SERVICES = ['블로그 기획·제작·운영', '브랜드 콘텐츠', '홈페이지·랜딩페이지 제작',
            '검색·AI 이해를 위한 정보 정비', 'AI 업무 적용 지원', 'AX 컨설팅']

def form(default, title, lead):
    svc = ''.join(f'<label><input type="checkbox" name="services" value="{s}"{" checked" if s == default else ""}> {s}</label>' for s in SERVICES)
    ch = ''.join(f'<label><input type="checkbox" name="channels" value="{c}"> {c}</label>' for c in ['네이버 블로그', '홈페이지', '인스타그램', '없음'])
    src = ''.join(f'<option>{o}</option>' for o in ['네이버 검색', '구글 검색', 'AI 답변', '블로그', '지인 소개', '기타'])
    return f'''<section class="block alt" id="contact" aria-labelledby="contact-h">
<div class="wrap">
  <p class="kicker">CONTACT</p>
  <h2 id="contact-h">{title}</h2>
  <p class="summary">{lead}</p>
  <form id="inquiry" class="form-box" novalidate>
    <div class="fgrid">
      <div class="field"><label for="f-org">병원명(회사명)<span class="req">*</span></label><input id="f-org" name="org" type="text" maxlength="100" autocomplete="organization"><span class="err" data-err="org"></span></div>
      <div class="field"><label for="f-dept">진료과(업종)<span class="req">*</span></label><input id="f-dept" name="dept" type="text" maxlength="50"><span class="err" data-err="dept"></span></div>
      <div class="field"><label for="f-name">담당자 이름<span class="req">*</span></label><input id="f-name" name="name" type="text" maxlength="30" autocomplete="name"><span class="err" data-err="name"></span></div>
      <div class="field"><label for="f-phone">연락처<span class="req">*</span></label><input id="f-phone" name="phone" type="tel" maxlength="15" autocomplete="tel" placeholder="010-0000-0000"><span class="err" data-err="phone"></span></div>
      <div class="field full"><label for="f-email">이메일</label><input id="f-email" name="email" type="email" maxlength="100" autocomplete="email"></div>
      <fieldset class="field full"><legend>현재 운영 채널</legend><div class="checks">{ch}</div></fieldset>
      <fieldset class="field full"><legend>필요한 서비스<span class="req">*</span></legend><div class="checks">{svc}</div><span class="err" data-err="services"></span></fieldset>
      <div class="field full"><label for="f-source">어떻게 알고 오셨나요?<span class="req">*</span></label><select id="f-source" name="source"><option value="">선택해 주세요</option>{src}</select><span class="err" data-err="source"></span></div>
      <div class="field full"><label for="f-msg">문의 내용</label><textarea id="f-msg" name="message" maxlength="2000" placeholder="현재 고민이나 필요한 내용을 자유롭게 적어 주세요."></textarea></div>
    </div>
    <div class="hp" aria-hidden="true"><label>웹사이트<input name="website" type="text" tabindex="-1" autocomplete="off"></label></div>
    <div class="consent">수집 항목: 병원명(회사명), 진료과(업종), 담당자 이름, 연락처, 이메일, 운영 채널, 필요 서비스, 유입 경로, 문의 내용 · 목적: 상담 및 견적 안내 · 보유 기간: 상담 목적 달성 시 지체 없이 파기(계약 체결 시 관계 법령에 따른 기간 보관) · <a href="/privacy/">전문 보기</a>
      <label><input type="checkbox" name="consent" value="Y"> 개인정보 수집·이용에 동의합니다.<span class="req">*</span></label>
      <span class="err" data-err="consent"></span>
    </div>
    <div class="form-actions"><button class="btn" type="submit">상담 신청하기</button><p class="form-msg" role="status" aria-live="polite"></p></div>
  </form>
  <p class="summary">전화 <a href="tel:010-2788-2911">010-2788-2911</a> · 이메일 <a href="mailto:pdshk08@gmail.com">pdshk08@gmail.com</a></p>
</div></section>'''

def float_ui():
    qa = re.findall(r'<summary>(.*?)</summary>\s*<p>(.*?)</p>', (SRC / 'marketing.html').read_text(encoding='utf-8'), re.S)
    data = json.dumps([{"q": q.strip(), "a": re.sub('<[^>]+>', '', a).strip()} for q, a in qa], ensure_ascii=False)
    return f'''<div class="float-ui">
  <button class="icon-btn chat-btn" type="button" aria-label="자주 묻는 질문 챗봇 열기" aria-expanded="false" aria-controls="chat-panel"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 11h.01M12 11h.01M15.5 11h.01"/></svg></button>
  <button class="icon-btn to-top" type="button" aria-label="맨 위로 이동"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></button>
</div>
<section class="chat-panel" id="chat-panel" role="dialog" aria-label="자주 묻는 질문 안내" aria-hidden="true">
  <div class="chat-head"><div><strong>마틴랩스 FAQ 안내</strong><small>자주 묻는 질문에 바로 답해 드립니다</small></div><button class="chat-close" type="button" aria-label="닫기">×</button></div>
  <div class="chat-body" aria-live="polite"></div>
  <form class="chat-form"><input type="text" placeholder="궁금한 내용을 입력하세요 (예: 비용)" aria-label="질문 입력" maxlength="100"><button type="submit">보내기</button></form>
</section>
<script type="application/json" id="faq-data">{data}</script>'''

def ga():
    if not GA_ID: return ''
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
            f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
            f'gtag("js",new Date());gtag("config","{GA_ID}");</script>')

def page(path, title, desc, body, extra_ld=()):
    assert len(desc) <= 80, (path, len(desc))
    graph = [ORG] + list(extra_ld)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="website"><meta property="og:site_name" content="마틴랩스 Martin Labs">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{BASE}{path}">
<meta property="og:locale" content="ko_KR">
<meta name="theme-color" content="#14382A">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700;900&display=swap">
<link rel="stylesheet" href="/assets/style.css">
{ga()}
<script type="application/ld+json">
{ld}
</script>
</head><body>
{header(path)}
<main id="main">
{body}
</main>
{FOOTER.replace('__FLOAT__', float_ui())}
</body></html>
'''

def crumb(path, name):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": BASE + path}]}

def faq_ld(body):
    qa = re.findall(r'<summary>(.*?)</summary>\s*<p>(.*?)</p>', body, re.S)
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q.strip(), "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a).strip()}}
        for q, a in qa]}

MARQUEE = [
  ['병원 블로그 기획', '환자 질문 기반 콘텐츠', '원고·이미지 제작', '의료광고 규정 검토', '발행·운영 점검', 'GEO 마케팅'],
  ['AI 업무 적용 지원', 'AX 컨설팅', '검색·AI 이해를 위한 정보 정비', '브랜드 콘텐츠', '홈페이지·랜딩페이지 제작', '첫 상담 무료'],
]
def marquee():
    rows = ''
    for i, words in enumerate(MARQUEE):
        items = ''.join(f'<span>{w}</span>' for w in words) * 2
        rows += f'<div class="marquee" aria-hidden="true"><div class="m-track{" rev" if i % 2 else ""}">{items}{items}</div></div>'
    return f'<div class="marquee-band">{rows}</div>'

# 이미지 자리: site/assets/img/<이름>.webp 가 있으면 히어로 도식 대신 이미지 사용
AI_PEOPLE = {'marketing'}  # 인물이 나오는 AI 생성 이미지: 캡션 표시
IMAGES = {'home': '정원과 함께 있는 현대적 병원 건물 입구', 'marketing': '진료 상담실에서 의사가 환자의 질문에 답하는 장면',
          'ax': 'AI를 업무에 적용하는 교육·실습 장면', 'consulting': '업무 현황을 진단하고 로드맵을 세우는 장면'}
HERO_BG = {'home'}  # 배경형 히어로 페이지, 나머지는 오른쪽 이미지 분할형
def hero_media(s, name):
    f = OUT / 'assets' / 'img' / f'{name}.webp'
    if not f.exists():
        return s
    if name in HERO_BG:
        # 배경형: 도식 제거, 데스크톱은 원본 비율 그대로(무잘림), 문구 가운데 정렬
        s = re.sub(r'\s*<svg class="flow".*?</svg>', '', s, count=1, flags=re.S)
        cap = '<p class="bg-cap">AI로 생성한 연출 이미지입니다</p>' if name in AI_PEOPLE else ''
        s = s.replace('<section class="hero"', f'<section class="hero hero-bg bg-{name}"', 1)
        s = s.replace('<div class="wrap hero-grid">', '<div class="wrap hero-center">', 1)
        s = s.replace('</div>\n</section>', f'</div>{cap}\n</section>', 1)
    else:
        # 분할형: 오른쪽 도식 자리에 이미지
        cap = '<figcaption>AI로 생성한 연출 이미지입니다</figcaption>' if name in AI_PEOPLE else ''
        s = re.sub(r'<svg class="flow".*?</svg>', f'<figure class="hero-fig"><img class="hero-img" src="/assets/img/{name}.webp" alt="{IMAGES[name]}" width="1536" height="1024" fetchpriority="high">{cap}</figure>', s, count=1, flags=re.S)
    return s

def load(name, marq=True, **forms):
    s = (SRC / name).read_text(encoding='utf-8')
    for k, v in forms.items(): s = s.replace('{{' + k + '}}', v)
    if marq: s = s.replace('</section>', '</section>\n' + marquee(), 1)
    n = name.replace('.html', '')
    return hero_media(s, n) if n in IMAGES else s

def write(path, html):
    f = OUT / (path.strip('/') + '/index.html' if path != '/' else 'index.html')
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding='utf-8')

PAGES = {}

# 홈
body = load('home.html', FORM=form('블로그 기획·제작·운영', '상담이 필요하신가요?',
       '관심 분야를 선택하고 남겨 주시면 내용을 확인한 뒤 연락드립니다. 첫 상담은 무료입니다.'))
write('/', page('/', '마틴랩스 | AX 컨설팅·AI 마케팅 전문 기업',
      'AX 컨설팅과 AI 마케팅으로 기업·기관·병원의 업무혁신과 사업 성장을 돕는 마틴랩스입니다.', body,
      [{"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "마틴랩스", "publisher": {"@id": BASE + "/#org"}, "inLanguage": "ko-KR"}]))

# 마케팅
body = load('marketing.html', FORM=form('블로그 기획·제작·운영', '병원 블로그 운영 상담 신청',
       '첫 상담은 무료입니다. 현재 운영 채널과 고민을 확인하고 필요한 서비스와 진행 방향을 안내합니다.'))
svc = [("병원 블로그 기획·제작·운영", "진료 분야와 환자 질문을 바탕으로 주제를 기획하고 원고·이미지 제작과 발행·운영 점검을 지원합니다."),
       ("브랜드 콘텐츠 제작", "병원 소개, 의료진 소개, 진료 과정 안내 등 병원 정보를 일관된 문장과 이미지로 정리합니다."),
       ("홈페이지·랜딩페이지 제작", "병원과 서비스 소개부터 상담 안내까지 이어지는 페이지를 기획하고 제작합니다."),
       ("검색·AI 이해를 위한 정보 정비", "병원·서비스 정보 정리, 질문에 답하는 콘텐츠 구조, 관리 권한이 있는 홈페이지의 메타정보·구조화 데이터·사이트맵 점검")]
write('/marketing/', page('/marketing/', '병원 블로그 마케팅·GEO 마케팅 | 마틴랩스',
      '환자 질문에 답하는 병원 블로그를 기획부터 운영까지 마틴랩스가 맡습니다. 첫 상담 무료.', body,
      [{"@type": "ProfessionalService", "@id": BASE + "/marketing/#service", "name": "마틴랩스 GEO 마케팅",
        "url": BASE + "/marketing/", "parentOrganization": {"@id": BASE + "/#org"},
        "telephone": "+82-10-2788-2911", "areaServed": "KR",
        "address": ORG["address"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "GEO 마케팅 실행 서비스", "itemListElement": [
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": d, "provider": {"@id": BASE + "/#org"}}} for n, d in svc]}},
       faq_ld(body), crumb('/marketing/', 'GEO 마케팅')]))

# AX 적용
def svc_page(path, src, default, ftitle, flead, title, desc, sname, sdesc, crumbname):
    body = load(src, FORM=form(default, ftitle, flead))
    write(path, page(path, title, desc, body, [
        {"@type": "Service", "@id": BASE + path + "#service", "name": sname, "description": sdesc, "serviceType": sname,
         "provider": {"@id": BASE + "/#org"}, "areaServed": "KR", "url": BASE + path},
        crumb(path, crumbname)]))

svc_page('/ax/', 'ax.html', 'AI 업무 적용 지원', 'AI 업무 적용 상담 신청',
    '대상 부서와 업무를 남겨 주시면 내용을 확인한 뒤 연락드립니다. 첫 상담은 무료입니다.',
    'AI 업무 적용 지원 | 교육·양식 설계·시범 적용 | 마틴랩스',
    '업무별 AI 활용 교육, 프롬프트·업무 양식 설계, 시범 적용까지 조직의 AI 업무 적용을 지원합니다.',
    'AI 업무 적용 지원', '업무별 AI 활용 교육, 프롬프트·업무 양식 설계, 시범 적용 지원', 'AI 업무 적용 지원')
svc_page('/consulting/', 'consulting.html', 'AX 컨설팅', 'AX 컨설팅 상담 신청',
    '조직 상황과 목표를 남겨 주시면 내용을 확인한 뒤 연락드립니다. 첫 상담은 무료입니다.',
    'AX 컨설팅 | 업무 진단·AI 과제 발굴·실행 로드맵 | 마틴랩스',
    '업무 현황 진단, AI 적용 과제 발굴, 도입 우선순위와 실행 계획 수립을 돕는 AX 컨설팅입니다.',
    'AX 컨설팅', '업무 현황 진단, AI 적용 과제 발굴, 도입 우선순위·실행 계획 수립', 'AX 컨설팅')

# 개인정보처리방침 (폼 없음 → 상담 버튼은 홈 폼으로)
EFFECTIVE = '2026년 10월 30일'  # 공개일 확정 후 입력
html = page('/privacy/', '개인정보처리방침 | 마틴랩스', '주식회사 마틴랩스의 개인정보 처리 목적, 항목, 보유 기간, 위탁, 정보주체 권리를 안내합니다.',
            load('privacy.html', marq=False, EFFECTIVE=EFFECTIVE), [crumb('/privacy/', '개인정보처리방침')])
write('/privacy/', html.replace('href="#contact"', 'href="/#contact"'))

# robots.txt · sitemap.xml · _headers
(OUT / 'robots.txt').write_text('''User-agent: *
Allow: /

User-agent: Googlebot
Allow: /
User-agent: Yeti
Allow: /
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /

Sitemap: https://martinlabs.kr/sitemap.xml
''', encoding='utf-8')
urls = ['/', '/marketing/', '/ax/', '/consulting/', '/privacy/']
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{BASE}{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
(OUT / '_headers').write_text('''/*
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://*.googletagmanager.com; style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com; connect-src 'self' https://script.google.com https://script.googleusercontent.com https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
''', encoding='utf-8')

print('built:', sorted(str(p.relative_to(OUT)) for p in OUT.rglob('*.html')))
