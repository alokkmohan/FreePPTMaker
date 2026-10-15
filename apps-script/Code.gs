/**
 * FreePPTMaker — AI proxy (Google Apps Script web app)
 *
 * The GitHub Pages website sends prompts here; this script calls the AI
 * provider with keys stored in Script Properties, so keys never reach the browser.
 *
 * Script Properties (Project Settings → Script properties):
 *   GROQ_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY   — set at least one
 *   PROVIDER_ORDER            (optional) default "groq,gemini,mistral"
 *   GROQ_MODEL / GEMINI_MODEL / MISTRAL_MODEL       (optional) override models
 *   MAX_REQUESTS_PER_MINUTE   (optional) default 30
 */

var DEFAULTS = {
  PROVIDER_ORDER: 'groq,gemini,mistral',
  GROQ_MODEL: 'llama-3.3-70b-versatile',
  GEMINI_MODEL: 'gemini-3.8-flash',
  MISTRAL_MODEL: 'mistral-small-latest',
  MAX_REQUESTS_PER_MINUTE: '30'
};
var MAX_INPUT_CHARS = 60000;

var KEY_NAMES = { groq: 'GROQ_API_KEY', gemini: 'GEMINI_API_KEY', mistral: 'MISTRAL_API_KEY' };

function prop_(name) {
  var v = PropertiesService.getScriptProperties().getProperty(name);
  return v || DEFAULTS[name] || '';
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return json_({ ok: true, service: 'FreePPTMaker AI proxy', providers: providers_() });
}

function doPost(e) {
  try {
    var body = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var messages = sanitize_(body.messages);
    rateLimit_();
    var r = generate_(messages, body.json !== false);
    return json_({ ok: true, text: r.text, provider: r.provider });
  } catch (err) {
    return json_({ ok: false, error: String((err && err.message) || err) });
  }
}

function sanitize_(messages) {
  if (!Array.isArray(messages) || !messages.length) throw new Error('No messages sent.');
  var total = 0;
  var out = messages.slice(0, 6).map(function (m) {
    var content = String((m && m.content) || '');
    total += content.length;
    return { role: m && m.role === 'system' ? 'system' : 'user', content: content };
  });
  if (total > MAX_INPUT_CHARS) throw new Error('Input is too long. Use a shorter document.');
  return out;
}

function rateLimit_() {
  var lock = LockService.getScriptLock();
  lock.waitLock(5000);
  try {
    var cache = CacheService.getScriptCache();
    var key = 'rl_' + Math.floor(Date.now() / 60000);
    var n = Number(cache.get(key) || 0) + 1;
    if (n > Number(prop_('MAX_REQUESTS_PER_MINUTE'))) {
      throw new Error('Server is busy right now. Please try again in a minute.');
    }
    cache.put(key, String(n), 120);
  } finally {
    lock.releaseLock();
  }
}

function providers_() {
  return prop_('PROVIDER_ORDER').split(',')
    .map(function (p) { return p.trim().toLowerCase(); })
    .filter(function (p) { return KEY_NAMES[p] && PropertiesService.getScriptProperties().getProperty(KEY_NAMES[p]); });
}

function generate_(messages, wantJson) {
  var order = providers_();
  if (!order.length) throw new Error('No AI API key is set in Script Properties.');
  var errors = [];
  for (var i = 0; i < order.length; i++) {
    var p = order[i];
    try {
      var text = CALLERS[p](messages, wantJson);
      if (text && String(text).trim()) return { text: text, provider: p };
      errors.push(p + ': empty response');
    } catch (err) {
      errors.push(p + ': ' + err.message);
    }
  }
  throw new Error('All AI providers failed — ' + errors.join(' | '));
}

// Model choice: GROQ_MODEL (set by you) → AUTO_GROQ_MODEL (found automatically) → default.
// When a provider says the model is retired, we look up its current models, save one, and retry.
function model_(p) {
  var props = PropertiesService.getScriptProperties();
  var name = p.toUpperCase() + '_MODEL';
  return props.getProperty(name) || props.getProperty('AUTO_' + name) || DEFAULTS[name];
}

function isModelError_(err) {
  return /HTTP (400|404)/.test(err.message) && /model/i.test(err.message);
}

var MODEL_FINDERS = {
  groq: function () {
    var data = fetchGet_('https://api.groq.com/openai/v1/models', { Authorization: 'Bearer ' + prop_('GROQ_API_KEY') });
    var ids = (data.data || []).map(function (m) { return m.id; })
      .filter(function (id) { return !/whisper|guard|tts|embed|playai|orpheus|prompt/i.test(id); });
    return pick_(ids, [/gpt-oss-120b/, /llama.*70b/, /llama-4/, /qwen/, /gpt-oss/, /./]);
  },
  gemini: function (err) {
    var hint = /use models\/([\w.\-]+)/.exec(err.message);
    if (hint) return hint[1];
    var data = fetchGet_('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200', { 'x-goog-api-key': prop_('GEMINI_API_KEY') });
    var ids = (data.models || [])
      .filter(function (m) { return (m.supportedGenerationMethods || []).indexOf('generateContent') >= 0; })
      .map(function (m) { return m.name.replace(/^models\//, ''); })
      .filter(function (id) { return /^gemini-[\d.]+-flash$/.test(id); })
      .sort(function (a, b) { return parseFloat(b.slice(7)) - parseFloat(a.slice(7)); });
    return ids[0];
  },
  mistral: function () { return 'mistral-small-latest'; }
};

function pick_(ids, prefs) {
  for (var i = 0; i < prefs.length; i++) {
    for (var j = 0; j < ids.length; j++) if (prefs[i].test(ids[j])) return ids[j];
  }
  return null;
}

function withModel_(p, call) {
  try {
    return call(model_(p));
  } catch (err) {
    if (!isModelError_(err)) throw err;
    var found = MODEL_FINDERS[p](err);
    if (!found || found === model_(p)) throw err;
    PropertiesService.getScriptProperties().setProperty('AUTO_' + p.toUpperCase() + '_MODEL', found);
    return call(found);
  }
}

var CALLERS = {
  groq: function (messages, wantJson) {
    return withModel_('groq', function (model) {
      return openAiStyle_('https://api.groq.com/openai/v1/chat/completions',
        prop_('GROQ_API_KEY'), model, messages, wantJson);
    });
  },
  mistral: function (messages, wantJson) {
    return withModel_('mistral', function (model) {
      return openAiStyle_('https://api.mistral.ai/v1/chat/completions',
        prop_('MISTRAL_API_KEY'), model, messages, wantJson);
    });
  },
  gemini: function (messages, wantJson) {
    return withModel_('gemini', function (model) { return gemini_(model, messages, wantJson); });
  }
};

function gemini_(model, messages, wantJson) {
  var join = function (role) {
    return messages.filter(function (m) { return m.role === role; })
      .map(function (m) { return m.content; }).join('\n\n');
  };
  var payload = {
    contents: [{ role: 'user', parts: [{ text: join('user') }] }],
    generationConfig: { temperature: 0.4, maxOutputTokens: 16384 }
  };
  var sys = join('system');
  if (sys) payload.systemInstruction = { parts: [{ text: sys }] };
  if (wantJson) payload.generationConfig.responseMimeType = 'application/json';
  var url = 'https://generativelanguage.googleapis.com/v1beta/models/' +
    encodeURIComponent(model) + ':generateContent';
  var data = fetchJson_(url, { 'x-goog-api-key': prop_('GEMINI_API_KEY') }, payload);
  var parts = (data.candidates && data.candidates[0] && data.candidates[0].content &&
    data.candidates[0].content.parts) || [];
  return parts.map(function (p) { return p.text || ''; }).join('');
}

function openAiStyle_(url, key, model, messages, wantJson) {
  var payload = { model: model, messages: messages, temperature: 0.4, max_tokens: 8000 };
  if (wantJson) payload.response_format = { type: 'json_object' };
  var data = fetchJson_(url, { Authorization: 'Bearer ' + key }, payload);
  return data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
}

function fetchGet_(url, headers) {
  return parse_(UrlFetchApp.fetch(url, { method: 'get', headers: headers, muteHttpExceptions: true }));
}

function fetchJson_(url, headers, payload) {
  return parse_(UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: headers,
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  }));
}

function parse_(res) {
  var code = res.getResponseCode();
  var text = res.getContentText();
  var data;
  try { data = JSON.parse(text); } catch (e) { data = null; }
  if (code !== 200 || !data) {
    var msg = data && data.error ? (data.error.message || JSON.stringify(data.error)) : text;
    throw new Error('HTTP ' + code + ' ' + String(msg).slice(0, 200));
  }
  return data;
}

/** Run this once from the editor to check your keys work. */
function testSetup() {
  Logger.log('Configured providers: ' + providers_().join(', '));
  var r = generate_([
    { role: 'system', content: 'Reply with one JSON object only.' },
    { role: 'user', content: 'Return JSON {"hello":"world"}' }
  ], true);
  Logger.log(r.provider + ' → ' + r.text);
}
