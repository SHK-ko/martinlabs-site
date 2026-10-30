/* 마틴랩스 공통 스크립트: 모바일 메뉴 + 문의 폼 */
(function () {
  // 문의 접수 주소 — Apps Script Web App 배포 후 교체 (DB 교체 시 sendInquiry만 수정)
  var SCRIPT_URL = 'https://script.google.com/macros/s/AKfycby-GWpXwKtUbzo8lXreRjsTrWW-gYeiFeMPMzkHqH4VW3acPsmhy6CSR6Q-SUzpnF66EA/exec';

  function track(name, params) {
    if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
  }

  // 스크롤 등장: 섹션 제목·카드·단계·표를 순차로 표시
  var targets = document.querySelectorAll('.block .kicker, .block h2, .block .summary, .block .note, .card, .steps li, .tbl-wrap, .facts li, .faq details, .form-box, .media');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (el) {
      var sibs = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
      el.style.transitionDelay = Math.min(sibs, 5) * 0.08 + 's';
      el.classList.add('reveal'); io.observe(el);
    });
  }

  // 숫자 카운트업 (예: 100+, 15+)
  var nums = document.querySelectorAll('.facts b');
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; cio.unobserve(e.target);
        var el = e.target, m = el.textContent.match(/^(\d+)(.*)$/); if (!m) return;
        var end = +m[1], suf = m[2], t0 = null;
        (function step(ts) { t0 = t0 || ts; var k = Math.min((ts - t0) / 1200, 1);
          el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3))) + suf; if (k < 1) requestAnimationFrame(step); })(performance.now());
      });
    }, { threshold: 0.6 });
    nums.forEach(function (n) { cio.observe(n); });
  }

  // 헤더 그림자·플로팅 상담 버튼
  var hd = document.querySelector('header.site'), fab = document.querySelector('.fab'), contact = document.getElementById('contact');
  function onScroll() {
    var y = window.scrollY;
    if (hd) hd.classList.toggle('scrolled', y > 10);
    if (fab) {
      var nearForm = contact && contact.getBoundingClientRect().top < window.innerHeight;
      fab.classList.toggle('show', y > 500 && !nearForm);
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // 맨 위로
  var topBtn = document.querySelector('.to-top');
  if (topBtn) topBtn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // FAQ 챗봇: FAQ 데이터를 질문 버튼·키워드 검색으로 안내 (AI 생성 답변 없음)
  (function () {
    var btn = document.querySelector('.chat-btn'), panel = document.getElementById('chat-panel'), dataEl = document.getElementById('faq-data');
    if (!btn || !panel || !dataEl) return;
    var faq = JSON.parse(dataEl.textContent), body = panel.querySelector('.chat-body'), started = false;
    var KEYS = [['업종', '병원 외', '기업', '기관'], ['비용', '가격', '견적', '얼마'], ['첫 상담', '무료', '상담'], ['자료', '준비'],
                ['절차', '발행', '심의', '규정', '검토'], ['보장', '상위', '노출', '환자 수', '순위'], ['결과', '보고', '지표', '확인']];
    function add(cls, html) { var d = document.createElement('div'); d.className = 'msg ' + cls; d.innerHTML = html; body.appendChild(d); body.scrollTop = body.scrollHeight; return d; }
    function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function chips() {
      var wrap = document.createElement('div'); wrap.className = 'chips';
      faq.forEach(function (f, i) { var c = document.createElement('button'); c.type = 'button'; c.className = 'chip'; c.textContent = f.q; c.onclick = function () { answer(i, f.q); }; wrap.appendChild(c); });
      var cta = document.createElement('button'); cta.type = 'button'; cta.className = 'chip cta'; cta.textContent = '상담 신청하기';
      cta.onclick = function () { close(); var c = document.getElementById('contact'); if (c) c.scrollIntoView({ behavior: 'smooth' }); else location.href = '/marketing/#contact'; track('click_cta', { position: 'chatbot' }); };
      wrap.appendChild(cta); body.appendChild(wrap); body.scrollTop = body.scrollHeight;
    }
    function answer(i, asked) {
      add('me', esc(asked)); add('bot', esc(faq[i].a));
      add('bot', '다른 질문도 골라 보세요.'); chips(); track('chatbot_question', { q: i + 1 });
    }
    function search(text) {
      var best = -1, score = 0;
      KEYS.forEach(function (ks, i) { var n = ks.filter(function (k) { return text.indexOf(k) > -1; }).length; if (n > score) { score = n; best = i; } });
      if (best > -1 && faq[best]) return answer(best, text);
      add('me', esc(text));
      add('bot', '정확한 답을 찾지 못했습니다. 아래 질문을 고르시거나, 상담 신청 또는 <a href="tel:010-2788-2911">010-2788-2911</a>로 문의해 주세요.'); chips();
    }
    function open() {
      panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false'); btn.setAttribute('aria-expanded', 'true');
      if (!started) { started = true; add('bot', '안녕하세요, 마틴랩스입니다. 자주 묻는 질문을 골라 보시거나 궁금한 내용을 입력해 주세요.'); chips(); }
      track('chatbot_open'); panel.querySelector('input').focus();
    }
    function close() { panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true'); btn.setAttribute('aria-expanded', 'false'); }
    btn.addEventListener('click', function () { panel.classList.contains('open') ? close() : open(); });
    panel.querySelector('.chat-close').addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    panel.querySelector('.chat-form').addEventListener('submit', function (e) {
      e.preventDefault(); var inp = this.querySelector('input'), v = inp.value.trim(); if (!v) return; inp.value = ''; search(v);
    });
  })();

  // 모바일 메뉴
  var btn = document.querySelector('.menu-btn');
  var nav = document.querySelector('nav.gnb');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // 전화·이메일·상담 버튼 클릭 측정
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('tel:') === 0) track('click_phone');
    else if (h.indexOf('mailto:') === 0) track('click_email');
    else if (a.hasAttribute('data-cta')) track('click_cta', { position: a.getAttribute('data-cta') });
  });

  // 폼
  var form = document.getElementById('inquiry');
  if (!form) return;

  // 제출 ID: 같은 입력의 재시도는 같은 ID로 보내 서버에서 중복 저장 차단
  var submissionId = null;
  function newId() {
    return (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
      : Date.now().toString(36) + Math.random().toString(36).slice(2);
  }
  // 동일 내용 재전송 = 같은 ID, 내용이 바뀐 재전송 = 새 ID + 관련 접수 ID, 접수 완료 후 = 새 ID
  var lastHash = null;
  var leadSent = {}; // GA4 generate_lead: 제출 ID당 최대 1회

  // 서버가 {ok:true,id} 를 돌려줘야만 성공으로 처리, 15초 시간 초과
  function sendInquiry(data) {
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 15000) : null;
    return fetch(SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(data),
      redirect: 'follow',
      signal: ctrl ? ctrl.signal : undefined
    }).then(function (r) { return r.json(); })
      .then(function (res) { if (!res || res.ok !== true) throw new Error('save_failed'); return res; })
      .finally(function () { if (timer) clearTimeout(timer); });
  }

  function setErr(name, msg) {
    var el = form.querySelector('[data-err="' + name + '"]');
    if (el) el.textContent = msg || '';
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = form.querySelector('.form-msg');
    msg.className = 'form-msg'; msg.textContent = '';

    // 허니팟: 사람에게 보이지 않는 칸이 채워지면 봇으로 판단
    if (form.website && form.website.value) return;

    var fd = new FormData(form);
    var data = {
      org: (fd.get('org') || '').trim(),
      dept: (fd.get('dept') || '').trim(),
      name: (fd.get('name') || '').trim(),
      phone: (fd.get('phone') || '').trim(),
      email: (fd.get('email') || '').trim(),
      channels: fd.getAll('channels').join(', '),
      services: fd.getAll('services').join(', '),
      source: fd.get('source') || '',
      message: (fd.get('message') || '').trim(),
      consent: fd.get('consent') ? 'Y' : '',
      page: location.href,
      submittedAt: new Date().toISOString()
    };

    var ok = true;
    [['org', '병원명(회사명)을 입력해 주세요.'], ['dept', '진료과(업종)를 입력해 주세요.'],
     ['name', '담당자 이름을 입력해 주세요.'], ['phone', '연락처를 입력해 주세요.'],
     ['services', '필요한 서비스를 하나 이상 선택해 주세요.'], ['source', '알게 된 경로를 선택해 주세요.'],
     ['consent', '개인정보 수집·이용에 동의해 주세요.']].forEach(function (r) {
      var bad = !data[r[0]];
      if (r[0] === 'phone' && data.phone && !/^[0-9\-+ ]{9,15}$/.test(data.phone)) bad = true;
      setErr(r[0], bad ? r[1] : '');
      if (bad) ok = false;
    });
    if (!ok) { var first = form.querySelector('.err:not(:empty)'); if (first) first.scrollIntoView({ block: 'center', behavior: 'smooth' }); return; }

    // 제출 ID 결정 (숨은 값 제외 항목으로 비교)
    var hash = JSON.stringify([data.org, data.dept, data.name, data.phone, data.email,
      data.channels, data.services, data.source, data.message, data.consent]);
    data.relatedId = '';
    if (submissionId && hash !== lastHash) { data.relatedId = submissionId; submissionId = null; }
    if (!submissionId) submissionId = newId();
    lastHash = hash;
    data.id = submissionId;

    var submit = form.querySelector('button[type=submit]');
    submit.disabled = true; submit.textContent = '보내는 중…';
    sendInquiry(data).then(function () {
      if (!leadSent[data.id]) { leadSent[data.id] = true; track('generate_lead', { page: location.pathname }); }
      form.reset(); submissionId = null; lastHash = null;
      msg.className = 'form-msg ok';
      msg.textContent = '상담 신청이 접수되었습니다. 내용을 확인한 뒤 연락드리겠습니다.';
    }).catch(function () {
      msg.className = 'form-msg no';
      msg.textContent = '전송에 실패했습니다. 010-2788-2911 또는 pdshk08@gmail.com으로 연락 주세요.';
    }).finally(function () {
      submit.disabled = false; submit.textContent = '상담 신청하기';
    });
  });
})();
