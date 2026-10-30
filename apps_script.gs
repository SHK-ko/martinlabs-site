/**
 * 마틴랩스 홈페이지 상담 신청 접수 (Google Apps Script Web App)
 * - 저장 확인 후 {ok:true,id} 응답, 같은 제출 ID 중복 저장 차단(LockService)
 * - 서버 검증(필수·길이·동의·서비스 목록), 수식 주입 방지
 * - 알림 메일 실패 시 접수 유지 + "알림 상태=실패" 기록, 10분마다 재발송
 * 설치: 폼연동_안내.md 참고. 최초 1회 setup() 실행.
 */
var SHEET_NAME = '문의접수';
var NOTIFY_TO = 'pdshk08@gmail.com';
var HEADERS = ['접수 시각', '제출 ID', '관련 접수 ID', '병원명(회사명)', '진료과(업종)', '담당자 이름', '연락처', '이메일',
  '현재 운영 채널', '필요한 서비스', '유입 경로', '문의 내용', '개인정보 동의', '제출 페이지', '브라우저 제출 시각',
  '알림 상태', '상태', '메모'];
var SERVICES = ['블로그 기획·제작·운영', '브랜드 콘텐츠', '홈페이지·랜딩페이지 제작', '검색·AI 이해를 위한 정보 정비', 'AI 업무 적용 지원', 'AX 컨설팅'];
var SOURCES = ['네이버 검색', '구글 검색', 'AI 답변', '블로그', '지인 소개', '기타'];
var COL = { id: 2, notify: 16 };

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#0B2419').setFontColor('#ffffff');
    var rule = SpreadsheetApp.newDataValidation().requireValueInList(['신규', '연락 완료', '계약', '보류'], true).build();
    sh.getRange(2, 17, 1000, 1).setDataValidation(rule);
  }
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'retryFailedMail') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('retryFailedMail').timeBased().everyMinutes(10).create();
}

function doPost(e) {
  var data;
  try { data = JSON.parse(e.postData.contents); } catch (err) { return out({ ok: false, error: 'bad_request' }); }

  var v = validate(data);
  if (v) return out({ ok: false, error: v });

  var lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return out({ ok: false, error: 'busy' });
  var row;
  try {
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    var last = sh.getLastRow();
    if (last > 1) {
      var found = sh.getRange(2, COL.id, last - 1, 1).createTextFinder(data.id).matchEntireCell(true).findNext();
      if (found) return out({ ok: true, id: data.id, duplicate: true }); // 이미 저장된 재전송
    }
    sh.appendRow([new Date(), data.id, data.relatedId || '', data.org, data.dept, data.name, data.phone, data.email || '',
      data.channels || '', data.services, data.source, data.message || '', 'Y', data.page || '', data.submittedAt || '',
      '대기', '신규', ''].map(safe));
    row = sh.getLastRow();
    SpreadsheetApp.flush();
  } finally {
    lock.releaseLock();
  }

  // 저장 이후 알림: 실패해도 접수는 유지
  var sh2 = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  try { sendMail(data); sh2.getRange(row, COL.notify).setValue('발송'); }
  catch (err) { sh2.getRange(row, COL.notify).setValue('실패'); }

  return out({ ok: true, id: data.id });
}

function validate(d) {
  function str(x) { return typeof x === 'string' ? x.trim() : ''; }
  ['id', 'org', 'dept', 'name', 'phone', 'services', 'source'].forEach(function (k) { d[k] = str(d[k]); });
  ['email', 'channels', 'message', 'relatedId', 'page', 'submittedAt'].forEach(function (k) { d[k] = str(d[k]); });
  if (!/^[A-Za-z0-9-]{8,64}$/.test(d.id)) return 'invalid_id';
  if (!d.org || d.org.length > 100) return 'org';
  if (!d.dept || d.dept.length > 50) return 'dept';
  if (!d.name || d.name.length > 30) return 'name';
  if (!/^[0-9\-+ ]{9,15}$/.test(d.phone)) return 'phone';
  if (d.email && (d.email.length > 100 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email))) return 'email';
  if (d.message.length > 2000) return 'message';
  if (d.consent !== 'Y') return 'consent';
  if (SOURCES.indexOf(d.source) < 0) return 'source';
  var svc = d.services.split(',').map(function (s) { return s.trim(); }).filter(String);
  if (!svc.length || svc.some(function (s) { return SERVICES.indexOf(s) < 0; })) return 'services';
  if (d.relatedId && !/^[A-Za-z0-9-]{8,64}$/.test(d.relatedId)) d.relatedId = '';
  return '';
}

// 스프레드시트 수식 주입 방지
function safe(v) {
  if (typeof v === 'string' && /^[=+\-@]/.test(v)) return "'" + v;
  return v;
}

function sendMail(d) {
  var body = [
    '홈페이지 상담 신청이 접수되었습니다.', '',
    '병원명(회사명): ' + d.org, '진료과(업종): ' + d.dept, '담당자: ' + d.name, '연락처: ' + d.phone,
    '이메일: ' + (d.email || '-'), '운영 채널: ' + (d.channels || '-'), '필요 서비스: ' + d.services,
    '유입 경로: ' + d.source, '', '문의 내용:', d.message || '-', '',
    '제출 ID: ' + d.id + (d.relatedId ? ' (관련 접수 ID: ' + d.relatedId + ')' : ''), '페이지: ' + d.page
  ].join('\n');
  MailApp.sendEmail({ to: NOTIFY_TO, subject: '[마틴랩스 상담 신청] ' + d.org + ' · ' + d.name, body: body });
}

// 10분마다: 알림 실패 건 재발송
function retryFailedMail() {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var last = sh.getLastRow(); if (last < 2) return;
  var rows = sh.getRange(2, 1, last - 1, HEADERS.length).getValues();
  rows.forEach(function (r, i) {
    if (r[COL.notify - 1] !== '실패') return;
    try {
      sendMail({ id: r[1], relatedId: r[2], org: r[3], dept: r[4], name: r[5], phone: r[6], email: r[7], channels: r[8],
        services: r[9], source: r[10], message: r[11], page: r[13] });
      sh.getRange(i + 2, COL.notify).setValue('재발송');
    } catch (err) { /* 다음 주기에 재시도 */ }
  });
}

function doGet() { return out({ ok: true, service: 'martinlabs-inquiry' }); }

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
