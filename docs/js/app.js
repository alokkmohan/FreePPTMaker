// UI wiring for FreePPTMaker.
(function () {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, ch =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  };

  const TRENDING = [
    'Artificial Intelligence in Education', 'Climate Change Solutions', 'Digital India',
    'Cyber Security Awareness', 'Mental Health at Workplace', 'Startup India',
    'Renewable Energy', 'Swachh Bharat Abhiyan'
  ];

  const state = {
    deck: null, opts: null, theme: 'modern', docs: [], chart: null, selected: -1, busy: false,
    brand: store.get('fpm_brand', {})
  };

  // ── helpers ──────────────────────────────────────────────────────
  function status(el, msg, kind) {
    el.className = 'status' + (kind ? ' ' + kind : '');
    el.innerHTML = msg ? (kind === 'busy' ? '<span class="spin"></span>' : '') + esc(msg) : '';
  }

  const activeBrand = () => {
    const b = Object.assign({}, state.brand);
    if (!b.useAccent) delete b.accent;
    return b;
  };

  const fileName = t => (String(t || 'presentation').replace(/[\\/:*?"<>|]+/g, '').replace(/\s+/g, '_').slice(0, 60) || 'presentation') + '.pptx';

  function blobToDataURL(blob) {
    return new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsDataURL(blob); });
  }

  async function fetchImage(prompt) {
    const q = encodeURIComponent(prompt + ', clean modern illustration, no text');
    const url = `https://image.pollinations.ai/prompt/${q}?width=960&height=1024&nologo=true&seed=${Math.floor(Math.random() * 1e6)}`;
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 45000);
    try {
      const r = await fetch(url, { signal: ctrl.signal });
      if (!r.ok) return null;
      const b = await r.blob();
      if (!b.type.startsWith('image/') || b.size < 5000) return null;
      return await blobToDataURL(b);
    } catch (e) { return null; } finally { clearTimeout(t); }
  }

  async function addImages(deck, onProgress) {
    const targets = deck.slides.filter(s => s.type === 'bullets' && s.image_prompt && (s.bullets || []).length <= 5).slice(0, 4);
    let done = 0;
    await Promise.all(targets.map(async s => {
      s.img = await fetchImage(s.image_prompt);
      onProgress(++done, targets.length);
    }));
  }

  // ── tabs ─────────────────────────────────────────────────────────
  function showTab(name) {
    $$('.tab').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
    $$('.panel').forEach(p => { p.hidden = p.id !== 'panel-' + name; });
  }
  $$('.tab').forEach(b => b.addEventListener('click', () => showTab(b.dataset.tab)));

  // ── theme pickers ────────────────────────────────────────────────
  function themePicker(el, onPick) {
    el.innerHTML = Object.entries(THEMES).map(([k, t]) =>
      `<button type="button" class="theme-opt" data-k="${k}" style="--bg:#${t.bg};--card:#${t.card};--accent:#${t.accent};--title:#${t.title}">
        <span class="tthumb"><i></i><b></b><em></em><em></em></span><span class="tname">${t.name}</span></button>`).join('');
    el.addEventListener('click', e => {
      const b = e.target.closest('.theme-opt');
      if (b) onPick(b.dataset.k);
    });
  }
  function markTheme() { $$('.theme-opt').forEach(b => b.classList.toggle('on', b.dataset.k === state.theme)); }
  const pickTheme = k => { state.theme = k; markTheme(); if (state.deck) renderPreview(); };
  themePicker($('#themes'), pickTheme);
  themePicker($('#result-themes'), pickTheme);
  markTheme();

  // ── trending chips ───────────────────────────────────────────────
  $('#trending').innerHTML = TRENDING.map(t => `<button type="button" class="chip">${esc(t)}</button>`).join('');
  $('#trending').addEventListener('click', e => {
    const c = e.target.closest('.chip');
    if (c) { $('#topic').value = c.textContent; $('#topic').focus(); }
  });

  // ── attachments ──────────────────────────────────────────────────
  function renderAttached() {
    const items = state.docs.map((d, i) => `<span class="file">📄 ${esc(d.name)} <button type="button" data-doc="${i}" aria-label="Remove">✕</button></span>`);
    if (state.chart) items.push(`<span class="file">📊 ${esc(state.chart.name)} <button type="button" data-chart aria-label="Remove">✕</button></span>`);
    $('#attached').innerHTML = items.join('');
    $('#chart-type-row').hidden = !state.chart;
  }
  $('#attached').addEventListener('click', e => {
    const b = e.target.closest('button');
    if (!b) return;
    if (b.hasAttribute('data-chart')) state.chart = null;
    else state.docs.splice(Number(b.dataset.doc), 1);
    renderAttached();
  });
  $('#files').addEventListener('change', async e => {
    const st = $('#status');
    for (const f of Array.from(e.target.files)) {
      try {
        status(st, 'Reading ' + f.name + '…', 'busy');
        if (Docs.isData(f)) state.chart = await Docs.table(f);
        else {
          const text = (await Docs.text(f)).replace(/\s+\n/g, '\n').trim();
          if (!text) throw new Error(f.name + ' has no readable text (scanned PDFs are not supported).');
          state.docs.push({ name: f.name, text });
        }
        status(st, '');
      } catch (err) { status(st, err.message, 'error'); }
    }
    e.target.value = '';
    renderAttached();
  });
  $('#chart-type').addEventListener('change', e => {
    if (state.chart) state.chart.chartType = e.target.value;
    if (state.deck) renderPreview();
  });

  // ── generate ─────────────────────────────────────────────────────
  function readOptions() {
    const max = (window.CONFIG || {}).MAX_DOC_CHARS || 15000;
    return {
      topic: $('#topic').value.trim(),
      lang: $('#lang').value,
      slides: Number($('#slides').value),
      tone: $('#tone').value,
      audience: $('#audience').value.trim(),
      extra: $('#extra').value.trim(),
      docText: state.docs.map(d => d.text).join('\n\n').slice(0, max),
      chart: state.chart,
      images: $('#images').checked
    };
  }

  function setBusy(b) {
    state.busy = b;
    ['#generate', '#regenerate', '#download', '#apply-edit', '#bulk-go'].forEach(s => { const el = $(s); if (el) el.disabled = b; });
  }

  async function generate(o) {
    const st = $('#status');
    if (!o.topic && !o.docText) { status(st, 'Enter a topic or attach a document.', 'error'); $('#topic').focus(); return; }
    setBusy(true);
    try {
      status(st, 'AI is writing your slides… (10–30 seconds)', 'busy');
      const deck = await AI.generateDeck(o);
      if (o.images) {
        await addImages(deck, (d, n) => status(st, `Adding images… ${d}/${n}`, 'busy'));
      }
      state.deck = deck;
      state.opts = o;
      state.selected = -1;
      showResult();
      status(st, `Done! ${deck.slides.length + 2} slides ready.`, 'ok');
    } catch (err) {
      status(st, err.message, 'error');
    } finally { setBusy(false); }
  }

  $('#create-form').addEventListener('submit', e => { e.preventDefault(); if (!state.busy) generate(readOptions()); });
  $('#regenerate').addEventListener('click', () => { if (!state.busy && state.opts) generate(Object.assign({}, state.opts, { chart: state.chart })); });

  // ── result / preview ─────────────────────────────────────────────
  function renderOpts() {
    return { theme: state.theme, lang: state.opts.lang, brand: activeBrand(), chart: state.chart };
  }

  function renderPreview() {
    Preview.render($('#preview'), state.deck, renderOpts(), state.selected);
    renderEditor();
  }

  function showResult() {
    $('#result').hidden = false;
    $('#deck-title').value = state.deck.title;
    $('#deck-subtitle').value = state.deck.subtitle;
    renderPreview();
    $('#result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  $('#deck-title').addEventListener('input', e => { state.deck.title = e.target.value; renderPreview(); });
  $('#deck-subtitle').addEventListener('input', e => { state.deck.subtitle = e.target.value; renderPreview(); });

  $('#preview').addEventListener('click', e => {
    const t = e.target.closest('.thumb[data-i]');
    if (!t) return;
    state.selected = Number(t.dataset.i);
    renderPreview();
    $('#editor').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    $('#edit-instruction').focus();
  });

  function renderEditor() {
    const ed = $('#editor');
    const s = state.deck && state.deck.slides[state.selected];
    ed.hidden = !s;
    if (!s) return;
    $('#editor-title').textContent = `Edit slide ${state.selected + 2}: ${s.title || ''}`;
    $('#edit-notes').innerHTML = s.notes ? `<b>Speaker notes:</b> ${esc(s.notes)}` : '';
    $('#move-up').disabled = state.selected === 0;
    $('#move-down').disabled = state.selected === state.deck.slides.length - 1;
    $('#delete-slide').disabled = state.deck.slides.length <= 1;
  }

  $('#close-editor').addEventListener('click', () => { state.selected = -1; renderPreview(); });
  $('#delete-slide').addEventListener('click', () => {
    state.deck.slides.splice(state.selected, 1);
    state.selected = -1;
    renderPreview();
  });
  function move(d) {
    const s = state.deck.slides, i = state.selected, j = i + d;
    if (j < 0 || j >= s.length) return;
    [s[i], s[j]] = [s[j], s[i]];
    state.selected = j;
    renderPreview();
  }
  $('#move-up').addEventListener('click', () => move(-1));
  $('#move-down').addEventListener('click', () => move(1));

  async function applyEdit() {
    const instr = $('#edit-instruction').value.trim();
    const st = $('#status');
    if (!instr || state.selected < 0 || state.busy) return;
    const idx = state.selected;
    setBusy(true);
    $('#apply-edit').textContent = 'Working…';
    try {
      const old = state.deck.slides[idx];
      const slide = await AI.editSlide(state.deck, idx, instr, { lang: state.opts.lang, chart: state.chart });
      if (slide.type === 'bullets' && old.img) slide.img = old.img;
      state.deck.slides[idx] = slide;
      $('#edit-instruction').value = '';
      renderPreview();
    } catch (err) {
      status(st, err.message, 'error');
      alert(err.message);
    } finally {
      setBusy(false);
      $('#apply-edit').textContent = 'Apply with AI';
    }
  }
  $('#apply-edit').addEventListener('click', applyEdit);
  $('#edit-instruction').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); applyEdit(); } });

  $('#download').addEventListener('click', async () => {
    const btn = $('#download');
    btn.disabled = true;
    try {
      const pptx = await Render.build(state.deck, renderOpts());
      await pptx.writeFile({ fileName: fileName(state.deck.title) });
    } catch (err) {
      alert('Could not create the PPTX: ' + err.message);
    } finally { btn.disabled = false; }
  });

  $('#share').href = 'https://wa.me/?text=' + encodeURIComponent('Make free AI presentations in seconds: ' + location.href.split('#')[0]);

  // ── branding ─────────────────────────────────────────────────────
  function loadBrandForm() {
    const b = state.brand;
    $('#b-company').value = b.company || '';
    $('#b-tagline').value = b.tagline || '';
    $('#b-presenter').value = b.presenter || '';
    $('#b-designation').value = b.designation || '';
    $('#b-accent').value = b.accent || '#1565c0';
    $('#b-use-accent').checked = !!b.useAccent;
    const img = $('#b-logo-preview');
    img.hidden = !b.logo; if (b.logo) img.src = b.logo;
    $('#b-logo-remove').hidden = !b.logo;
  }

  function resizeLogo(file) {
    return new Promise((res, rej) => {
      const img = new Image();
      img.onload = () => {
        const scale = Math.min(1, 500 / Math.max(img.width, img.height));
        const cv = document.createElement('canvas');
        cv.width = Math.round(img.width * scale); cv.height = Math.round(img.height * scale);
        cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
        URL.revokeObjectURL(img.src);
        res(cv.toDataURL('image/png'));
      };
      img.onerror = () => rej(new Error('Could not read that image.'));
      img.src = URL.createObjectURL(file);
    });
  }

  let pendingLogo;
  $('#b-logo').addEventListener('change', async e => {
    const f = e.target.files[0];
    if (!f) return;
    try {
      pendingLogo = await resizeLogo(f);
      const img = $('#b-logo-preview'); img.src = pendingLogo; img.hidden = false;
      $('#b-logo-remove').hidden = false;
    } catch (err) { $('#brand-status').textContent = err.message; }
    e.target.value = '';
  });
  $('#b-logo-remove').addEventListener('click', () => {
    pendingLogo = null;
    $('#b-logo-preview').hidden = true;
    $('#b-logo-remove').hidden = true;
  });

  $('#brand-form').addEventListener('submit', e => {
    e.preventDefault();
    const b = {
      company: $('#b-company').value.trim(),
      tagline: $('#b-tagline').value.trim(),
      presenter: $('#b-presenter').value.trim(),
      designation: $('#b-designation').value.trim(),
      accent: $('#b-accent').value,
      useAccent: $('#b-use-accent').checked,
      logo: pendingLogo === undefined ? state.brand.logo : pendingLogo
    };
    if (!b.logo) delete b.logo;
    state.brand = b;
    pendingLogo = undefined;
    const saved = store.set('fpm_brand', b);
    $('#brand-status').textContent = saved ? 'Saved ✓ Applied to all new PPTs.' : 'Applied for this visit (browser storage is unavailable).';
    if (state.deck) renderPreview();
  });
  $('#b-clear').addEventListener('click', () => {
    state.brand = {}; pendingLogo = undefined;
    store.set('fpm_brand', {});
    loadBrandForm();
    $('#brand-status').textContent = 'Branding cleared.';
    if (state.deck) renderPreview();
  });
  loadBrandForm();

  // ── bulk ─────────────────────────────────────────────────────────
  let bulkRows = [];
  const LANGS = ['English', 'Hindi', 'Gujarati', 'Tamil', 'Bengali', 'Marathi', 'Telugu', 'Kannada'];

  $('#bulk-sample').addEventListener('click', () => {
    const csv = 'Topic,Theme,Slides,Language\nArtificial Intelligence in Education,modern,8,English\nClimate Change Solutions,nature,10,Hindi\nCyber Security Awareness,dark,8,English\n';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'bulk_sample.csv';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });

  $('#bulk-file').addEventListener('change', async e => {
    const f = e.target.files[0];
    e.target.value = '';
    if (!f) return;
    const st = $('#bulk-status');
    const parsed = Papa.parse(await f.text(), { header: true, skipEmptyLines: true, transformHeader: h => h.trim().toLowerCase() });
    const max = (window.CONFIG || {}).MAX_BULK || 10;
    bulkRows = parsed.data.filter(r => (r.topic || '').trim()).slice(0, max).map(r => {
      const theme = String(r.theme || 'modern').trim().toLowerCase();
      const lang = LANGS.find(l => l.toLowerCase() === String(r.language || '').trim().toLowerCase()) || 'English';
      return {
        topic: r.topic.trim().slice(0, 300),
        theme: THEMES[theme] ? theme : 'modern',
        slides: Math.min(20, Math.max(4, parseInt(r.slides, 10) || 8)),
        lang
      };
    });
    if (!bulkRows.length) {
      $('#bulk-table').innerHTML = '';
      $('#bulk-go').hidden = true;
      status(st, 'No rows found. The CSV needs a "Topic" column.', 'error');
      return;
    }
    $('#bulk-table').innerHTML = `<table><thead><tr><th>#</th><th>Topic</th><th>Theme</th><th>Slides</th><th>Language</th><th>Status</th></tr></thead><tbody>${
      bulkRows.map((r, i) => `<tr><td>${i + 1}</td><td>${esc(r.topic)}</td><td>${THEMES[r.theme].name}</td><td>${r.slides}</td><td>${r.lang}</td><td data-st="${i}">Waiting</td></tr>`).join('')
    }</tbody></table>`;
    $('#bulk-go').hidden = false;
    status(st, `${bulkRows.length} topics loaded${parsed.data.length > max ? ` (only the first ${max} are used)` : ''}.`, 'ok');
  });

  $('#bulk-go').addEventListener('click', async () => {
    if (state.busy || !bulkRows.length) return;
    const st = $('#bulk-status');
    const zip = new JSZip();
    const brand = activeBrand();
    const used = new Set();
    let ok = 0;
    setBusy(true);
    for (let i = 0; i < bulkRows.length; i++) {
      const r = bulkRows[i], cell = $(`[data-st="${i}"]`);
      status(st, `Generating ${i + 1} of ${bulkRows.length}: ${r.topic}`, 'busy');
      cell.textContent = 'Working…';
      try {
        const deck = await AI.generateDeck({ topic: r.topic, lang: r.lang, slides: r.slides, tone: 'Professional' });
        const pptx = await Render.build(deck, { theme: r.theme, lang: r.lang, brand });
        const blob = await pptx.write({ outputType: 'blob' });
        let name = fileName(r.topic);
        for (let n = 2; used.has(name); n++) name = fileName(r.topic + '_' + n);
        used.add(name);
        zip.file(name, blob);
        cell.textContent = '✓ Done'; ok++;
      } catch (err) {
        cell.textContent = '✕ ' + err.message.slice(0, 60);
      }
    }
    setBusy(false);
    if (!ok) { status(st, 'All presentations failed. Please try again.', 'error'); return; }
    const out = await zip.generateAsync({ type: 'blob' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(out);
    a.download = 'bulk_presentations.zip';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    status(st, `${ok} of ${bulkRows.length} presentations ready. ZIP downloaded.`, 'ok');
  });

  if (!(window.CONFIG || {}).APPS_SCRIPT_URL) {
    status($('#status'), 'Setup needed: add your Apps Script URL in docs/js/config.js.', 'error');
  }
})();
