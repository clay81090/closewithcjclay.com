/**
 * Sample Google Apps Script for HTSA enrollment web app deployments.
 *
 * Deploy: Extensions → Apps Script → Deploy → Web app.
 * Recommended: Execute as: Me · Who has access: Anyone (so static HTML POSTs succeed).
 *
 * Script properties you can set via Project Settings → Script properties:
 *   ENROLLMENT_LOG_SHEET_ID = Google Sheet ID holding the log tab
 *   SHEET_TAB_NAME          = Tab name (default "EnrollmentLog" or first sheet)
 *   CC_CHRISTIAN_EMAIL      = Ops / Christian copy destination (optional)
 *
 * The static pages send POST payload as application/x-www-form-urlencoded
 * with a single field "payload" whose value is JSON stringified metadata.
 */

function doPost(e) {
  var data;
  try {
    data = parseEnrollmentPayload_(e);
  } catch (err) {
    return respondJson_({ success: false, error: String(err && err.message ? err.message : err) });
  }

  try {
    routeEnrollmentAction_(data);
  } catch (err2) {
    return respondJson_({ success: false, error: String(err2 && err2.message ? err2.message : err2) });
  }

  return respondJson_({ success: true, receivedAction: data.action || 'legacy' });
}

function parseEnrollmentPayload_(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('Missing POST body');
  }
  var type = String(e.postData.type || '').toLowerCase();

  // Legacy: raw application/json POST (older testers)
  if (type.indexOf('application/json') !== -1) {
    return JSON.parse(e.postData.contents);
  }

  // Preferred: browse sends application/x-www-form-urlencoded with payload=<json>
  if (e.parameter && e.parameter.payload) {
    return JSON.parse(String(e.parameter.payload));
  }

  // Fallback: decode first payload= pair manually
  var raw = e.postData.contents;
  if (raw.indexOf('payload=') === 0 || raw.split('&')[0].indexOf('payload=') === 0) {
    var pair = raw.split('&')[0];
    var encoded = pair.replace(/^payload=/, '');
    var decoded = decodeURIComponent(encoded.replace(/\+/g, ' '));
    return JSON.parse(decoded);
  }

  throw new Error('Could not locate JSON payload');

}

function routeEnrollmentAction_(payload) {
  var action = String(payload.action || '');

  switch (action) {
    case 'recordTermsAgreement':
      appendEnrollmentRow_('terms_agreement', payload);
      break;
    case 'recordSimulatedPayment':
      appendEnrollmentRow_('simulated_payment', payload);
      sendPracticeReceipts_(payload);
      break;
    default:
      appendEnrollmentRow_('legacy_unknown', payload);
  }
}

function appendEnrollmentRow_(kind, payload) {
  var props = PropertiesService.getScriptProperties();
  var sid = props.getProperty('ENROLLMENT_LOG_SHEET_ID');
  if (!sid) {
    Logger.log('ENROLLMENT_LOG_SHEET_ID not configured — skipping sheet row. Payload stub: %s', JSON.stringify(payload));
    return;
  }

  var tabName = props.getProperty('SHEET_TAB_NAME') || 'EnrollmentLog';
  var ss = SpreadsheetApp.openById(sid);
  var sheet = ss.getSheetByName(tabName) || ss.getSheets()[0];
  sheet.appendRow([
    new Date(),
    kind,
    payload.clientSlug || '',
    payload.fullName || '',
    payload.email || '',
    payload.phone || '',
    payload.enrollmentPageUrl || '',
    payload.termsVersion || '',
    JSON.stringify(payload)
  ]);
}

/**
 * Sends practice-payment notifications only — customize / guard for production webhooks separately.
 */
function sendPracticeReceipts_(payload) {
  if (!payload || !payload.practicePage) {
    return;
  }
  var primary = payload.receiptEmailPrimary || Session.getEffectiveUser().getEmail();
  var christian = PropertiesService.getScriptProperties().getProperty('CC_CHRISTIAN_EMAIL');
  var body = Utilities.formatString(
      'Practice / simulated enrollment signal\nSlug: %s\nAction: recordSimulatedPayment\nFull payload:\n%s',
      String(payload.clientSlug || ''),
      JSON.stringify(payload, null, 2)
  );

  MailApp.sendEmail({
    to: primary,
    subject: '[Practice] HTSA simulated payment recorded',
    body: body
  });

  if (christian) {
    MailApp.sendEmail({
      to: christian,
      subject: '[Practice HTSA] FYI simulated enrollment ping',
      body: body
    });
  }
}

function respondJson_(obj) {
  return ContentService
      .createTextOutput(JSON.stringify(obj))
      .setMimeType(ContentService.MimeType.JSON);
}
