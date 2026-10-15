// HTML preview of a deck that mirrors the PPTX layouts.
(function () {
  'use strict';

  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, ch =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

  function vars(T, F) {
    const font = F === 'Calibri' ? "Calibri, Carlito, 'Segoe UI', sans-serif" : "'Nirmala UI', 'Noto Sans', sans-serif";
    return `--bg:#${T.bg};--card:#${T.card};--card2:#${T.card2};--title:#${T.title};--body:#${T.body};` +
      `--accent:#${T.accent};--accent2:#${T.accent2};--muted:#${T.muted};` +
      `--on1:#${Render.onColor(T.accent)};--on2:#${Render.onColor(T.accent2)};--font:${font}`;
  }

  function footer(B, num) {
    const foot = [B.company, B.tagline].filter(Boolean).join('  |  ');
    return `<div class="sp-foot"><span>${esc(foot)}</span><span>${num || ''}</span></div>`;
  }

  function chartBars(ch) {
    if (!ch || !ch.series.length) return '<div class="sp-chart-empty">Chart</div>';
    const vals = ch.series[0].values, max = Math.max(1, ...vals.map(v => Math.abs(v)));
    return `<div class="sp-bars">${vals.slice(0, 12).map((v, i) =>
      `<i style="height:${Math.max(4, Math.abs(v) / max * 100)}%;background:var(${i % 2 ? '--accent2' : '--accent'})"></i>`).join('')}</div>`;
  }

  const BODY = {
    bullets: d => `<div class="sp-body"><div class="sp-list">${(d.bullets || []).map((b, i) =>
      `<div class="sp-card${i % 2 ? ' alt' : ''}">${esc(b)}</div>`).join('')}</div>${d.img ? `<img class="sp-img" src="${esc(d.img)}" alt="">` : ''}</div>`,
    two_column: d => `<div class="sp-body">${[d.left, d.right].map((c, i) =>
      `<div class="sp-col"><div class="sp-band${i ? ' alt' : ''}">${esc(c.heading)}</div><ul>${c.bullets.map(b => `<li>${esc(b)}</li>`).join('')}</ul></div>`).join('')}</div>`,
    stats: d => `<div class="sp-body sp-stats">${d.stats.map(s =>
      `<div class="sp-stat"><b>${esc(s.value)}</b><hr><span>${esc(s.label)}</span></div>`).join('')}</div>`,
    timeline: d => `<div class="sp-body sp-tl"><div class="sp-tl-line"></div>${d.steps.map((s, i) =>
      `<div class="sp-step"><i class="${i % 2 ? 'alt' : ''}">${i + 1}</i><b>${esc(s.label)}</b><span>${esc(s.text)}</span></div>`).join('')}</div>`,
    quote: d => `<div class="sp-quote"><span class="q">“</span><p>${esc(d.quote)}</p>${d.author ? `<cite>— ${esc(d.author)}</cite>` : ''}</div>`,
    chart: (d, o) => `<div class="sp-body"><div class="sp-chartbox">${chartBars(o.chart)}</div>${(d.bullets || []).length ?
      `<div class="sp-col sp-ins"><ul>${d.bullets.map(b => `<li>${esc(b)}</li>`).join('')}</ul></div>` : ''}</div>`
  };

  function contentSlide(d, o, num) {
    const B = o.brand || {};
    const body = (BODY[d.type] || BODY.bullets)(d, o);
    const title = d.type === 'quote' ? '' : `<div class="sp-h">${esc(d.title)}</div>`;
    return `<div class="sp" style="${o.vars}"><div class="sp-bar"></div>${B.logo ? `<img class="sp-logo" src="${esc(B.logo)}" alt="">` : ''}${title}${body}${footer(B, num)}</div>`;
  }

  function titleSlide(deck, o) {
    const B = o.brand || {};
    return `<div class="sp sp-title" style="${o.vars}"><i class="c1"></i><i class="c2"></i><i class="side"></i>
      ${B.logo ? `<img class="sp-tlogo" src="${esc(B.logo)}" alt="">` : ''}
      <div class="sp-tt">${esc(deck.title)}</div><div class="sp-tbar"></div>
      <div class="sp-ts">${esc(deck.subtitle)}</div>
      ${B.presenter ? `<div class="sp-tp"><b>${esc(B.presenter)}</b><span>${esc(B.designation)}</span></div>` : ''}
      <div class="sp-tf">${esc([B.company, B.tagline].filter(Boolean).join('  |  '))}</div></div>`;
  }

  function closingSlide(deck, o, num) {
    const B = o.brand || {};
    const sub = B.presenter ? [B.presenter, B.designation].filter(Boolean).join(', ') : deck.title;
    return `<div class="sp" style="${o.vars}"><div class="sp-bar"></div>${B.logo ? `<img class="sp-logo" src="${esc(B.logo)}" alt="">` : ''}
      <div class="sp-end"><b>${esc(Render.THANKS[o.lang] || Render.THANKS.English)}</b><hr><span>${esc(sub)}</span></div>${footer(B, num)}</div>`;
  }

  const LABEL = { bullets: 'Bullets', two_column: 'Two columns', stats: 'Stats', timeline: 'Timeline', quote: 'Quote', chart: 'Chart' };

  window.Preview = {
    render(el, deck, opts, selected) {
      const T = Render.themeFor(opts.theme, opts.brand);
      const o = Object.assign({}, opts, { vars: vars(T, Render.fontFor(opts.lang)) });
      const n = deck.slides.length;
      const items = [`<div class="thumb fixed"><div class="thumb-cap">1 · Title</div>${titleSlide(deck, o)}</div>`]
        .concat(deck.slides.map((d, i) => `<button type="button" class="thumb${i === selected ? ' sel' : ''}" data-i="${i}">
          <div class="thumb-cap">${i + 2} · ${LABEL[d.type] || 'Slide'}</div>${contentSlide(d, o, i + 2)}</button>`))
        .concat(`<div class="thumb fixed"><div class="thumb-cap">${n + 2} · Closing</div>${closingSlide(deck, o, n + 2)}</div>`);
      el.innerHTML = items.join('');
    }
  };
})();
