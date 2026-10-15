// Builds a .pptx from a deck object with PptxGenJS (runs fully in the browser).
(function () {
  'use strict';

  const W = 13.333, H = 7.5;
  const THANKS = {
    English: 'Thank You', Hindi: 'धन्यवाद', Gujarati: 'આભાર', Tamil: 'நன்றி', Bengali: 'ধন্যবাদ',
    Marathi: 'धन्यवाद', Telugu: 'ధన్యవాదాలు', Kannada: 'ಧನ್ಯವಾದಗಳು'
  };
  const EXTRA_COLORS = ['5C6BC0', '26A69A', 'FFA726', 'EF5350', 'AB47BC', '8D6E63', '78909C'];

  const fontFor = lang => (!lang || lang === 'English') ? 'Calibri' : 'Nirmala UI';
  const imgData = d => String(d).replace(/^data:/, '');

  function onColor(hex) {
    const n = parseInt(hex, 16), r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.62 ? '1A1A1A' : 'FFFFFF';
  }

  function themeFor(key, brand) {
    const t = Object.assign({}, THEMES[key] || THEMES.modern);
    const a = brand && brand.accent;
    if (a && /^#?[0-9a-f]{6}$/i.test(a)) t.accent = a.replace('#', '').toUpperCase();
    return t;
  }

  // ── shared pieces ────────────────────────────────────────────────
  function frame(c, num) {
    const { pptx, T, F, B } = c;
    const s = pptx.addSlide();
    s.background = { color: T.bg };
    s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.12, fill: { color: T.accent }, line: { type: 'none' } });
    if (B.logo) s.addImage({ data: imgData(B.logo), x: W - 1.6, y: 0.3, w: 1.1, h: 0.62, sizing: { type: 'contain', w: 1.1, h: 0.62 } });
    const foot = [B.company, B.tagline].filter(Boolean).join('  |  ');
    if (foot) s.addText(foot, { x: 0.6, y: H - 0.55, w: 9, h: 0.35, fontSize: 10, color: T.muted, fontFace: F, margin: 0 });
    if (num) s.addText(String(num), { x: W - 1.3, y: H - 0.55, w: 0.7, h: 0.35, fontSize: 10, color: T.muted, fontFace: F, align: 'right', margin: 0 });
    return s;
  }

  function heading(c, s, title) {
    const { pptx, T, F } = c;
    s.addText(title || '', {
      x: 0.6, y: 0.35, w: W - 2.5, h: 0.95, fontSize: (title || '').length > 40 ? 24 : 28,
      bold: true, color: T.title, fontFace: F, valign: 'middle', margin: 0
    });
    s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 1.32, w: 1.1, h: 0.06, fill: { color: T.accent }, line: { type: 'none' } });
  }

  function card(c, s, x, y, w, h) {
    s.addShape(c.pptx.ShapeType.roundRect, {
      x, y, w, h, rectRadius: 0.08, fill: { color: c.T.card }, line: { color: c.T.card2, width: 0.75 }
    });
  }

  function bulletRuns(items, c) {
    return items.map(t => ({ text: t, options: { bullet: { indent: 18 }, paraSpaceAfter: 10, color: c.T.body } }));
  }

  // ── layouts ──────────────────────────────────────────────────────
  const DRAW = {
    bullets(c, s, d) {
      const { pptx, T, F } = c;
      const items = (d.bullets || []).slice(0, 6);
      const hasImg = !!d.img;
      const x = 0.6, w = hasImg ? 7.2 : W - 1.2, y0 = 1.65, avail = 4.95, gap = 0.16, n = Math.max(1, items.length);
      const h = Math.min(1.15, (avail - gap * (n - 1)) / n);
      const fs = (n <= 4 ? 18 : 16) - (items.some(b => b.length > 100) ? 2 : 0);
      items.forEach((b, i) => {
        const y = y0 + i * (h + gap);
        card(c, s, x, y, w, h);
        s.addShape(pptx.ShapeType.rect, { x, y, w: 0.09, h, fill: { color: i % 2 ? T.accent2 : T.accent }, line: { type: 'none' } });
        s.addText(b, { x: x + 0.3, y, w: w - 0.45, h, fontSize: fs, color: T.body, fontFace: F, valign: 'middle', margin: 0 });
      });
      if (hasImg) s.addImage({ data: imgData(d.img), x: 8.1, y: 1.65, w: 4.63, h: 4.95, sizing: { type: 'cover', w: 4.63, h: 4.95 } });
    },

    two_column(c, s, d) {
      const { pptx, T, F } = c;
      const rows = Math.max(d.left.bullets.length, d.right.bullets.length);
      const h = Math.min(4.95, 1.6 + rows * 0.7);
      [d.left, d.right].forEach((col, i) => {
        const x = 0.6 + i * 6.17, w = 5.97, y = 1.65, band = i ? T.accent2 : T.accent;
        card(c, s, x, y, w, h);
        s.addShape(pptx.ShapeType.rect, { x, y, w, h: 0.7, fill: { color: band }, line: { type: 'none' } });
        s.addText(col.heading || '', { x: x + 0.3, y, w: w - 0.6, h: 0.7, fontSize: 18, bold: true, color: onColor(band), fontFace: F, valign: 'middle', margin: 0 });
        s.addText(bulletRuns(col.bullets, c), { x: x + 0.3, y: y + 0.9, w: w - 0.6, h: h - 1.1, fontSize: 16, fontFace: F, valign: 'top', margin: 0 });
      });
    },

    stats(c, s, d) {
      const { pptx, T, F } = c;
      const n = d.stats.length, gap = 0.3, w = (W - 1.2 - gap * (n - 1)) / n, y = 2.0, h = 3.6;
      d.stats.forEach((st, i) => {
        const x = 0.6 + i * (w + gap);
        card(c, s, x, y, w, h);
        s.addText(st.value, { x, y: y + 0.35, w, h: 1.4, fontSize: n > 3 ? 40 : 48, bold: true, color: T.accent, fontFace: F, align: 'center', valign: 'middle', margin: 0 });
        s.addShape(pptx.ShapeType.rect, { x: x + w / 2 - 0.4, y: y + 1.9, w: 0.8, h: 0.05, fill: { color: T.accent2 }, line: { type: 'none' } });
        s.addText(st.label, { x: x + 0.25, y: y + 2.1, w: w - 0.5, h: 1.3, fontSize: 16, color: T.body, fontFace: F, align: 'center', valign: 'top', margin: 0 });
      });
    },

    timeline(c, s, d) {
      const { pptx, T, F } = c;
      const n = d.steps.length, colW = (W - 1.2) / n, lineY = 3.2;
      s.addShape(pptx.ShapeType.rect, { x: 0.6 + colW / 2, y: lineY - 0.03, w: colW * (n - 1), h: 0.06, fill: { color: T.card2 }, line: { type: 'none' } });
      d.steps.forEach((st, i) => {
        const cx = 0.6 + colW * (i + 0.5), col = i % 2 ? T.accent2 : T.accent;
        s.addShape(pptx.ShapeType.ellipse, { x: cx - 0.3, y: lineY - 0.3, w: 0.6, h: 0.6, fill: { color: col }, line: { color: T.bg, width: 3 } });
        s.addText(String(i + 1), { x: cx - 0.3, y: lineY - 0.3, w: 0.6, h: 0.6, fontSize: 16, bold: true, color: onColor(col), align: 'center', valign: 'middle', margin: 0, fontFace: F });
        s.addText(st.label, { x: cx - colW / 2 + 0.1, y: lineY + 0.5, w: colW - 0.2, h: 0.6, fontSize: 16, bold: true, color: T.title, align: 'center', valign: 'middle', margin: 0, fontFace: F });
        s.addText(st.text, { x: cx - colW / 2 + 0.15, y: lineY + 1.15, w: colW - 0.3, h: 2.1, fontSize: n > 4 ? 13 : 14, color: T.body, align: 'center', valign: 'top', margin: 0, fontFace: F });
      });
    },

    quote(c, s, d) {
      const { T, F } = c;
      s.addText('“', { x: 0.8, y: 1.4, w: 1.5, h: 1.5, fontSize: 120, bold: true, color: T.accent, fontFace: 'Georgia', margin: 0 });
      s.addText(d.quote, { x: 1.6, y: 2.0, w: W - 3.2, h: 2.9, fontSize: d.quote.length > 180 ? 22 : 28, italic: true, color: T.title, fontFace: F, align: 'center', valign: 'middle', margin: 0 });
      if (d.author) s.addText('— ' + d.author, { x: 1.6, y: 5.05, w: W - 3.2, h: 0.6, fontSize: 18, bold: true, color: T.accent, fontFace: F, align: 'center', margin: 0 });
    },

    chart(c, s, d) {
      const { pptx, T, F } = c;
      const ch = c.chart;
      if (!ch || !ch.series || !ch.series.length) return DRAW.bullets(c, s, d);
      const kind = { bar: pptx.ChartType.bar, line: pptx.ChartType.line, pie: pptx.ChartType.pie }[ch.chartType] || pptx.ChartType.bar;
      const isPie = ch.chartType === 'pie';
      const data = (isPie ? ch.series.slice(0, 1) : ch.series).map(se => ({ name: se.name, labels: ch.labels, values: se.values }));
      const ins = (d.bullets || []).length > 0;
      const cw = ins ? 8.0 : W - 1.2;
      s.addChart(kind, data, {
        x: 0.6, y: 1.6, w: cw, h: 5.1,
        chartColors: isPie || data.length > 1 ? [T.accent, T.accent2].concat(EXTRA_COLORS) : [T.accent],
        showLegend: isPie || data.length > 1, legendPos: 'b', legendColor: T.body, legendFontFace: F,
        catAxisLabelColor: T.body, valAxisLabelColor: T.body, catAxisLabelFontFace: F, valAxisLabelFontFace: F,
        valGridLine: { color: T.card2, size: 0.5 }, showPercent: isPie, dataLabelColor: 'FFFFFF',
        barGapWidthPct: 60, lineSize: 3
      });
      if (ins) {
        card(c, s, 8.9, 1.6, W - 9.5, 5.1);
        s.addText(bulletRuns(d.bullets, c), { x: 9.15, y: 1.85, w: W - 10.0, h: 4.6, fontSize: 15, fontFace: F, valign: 'top', margin: 0 });
      }
    }
  };

  // ── title & closing ──────────────────────────────────────────────
  function titleSlide(c, deck) {
    const { pptx, T, F, B } = c;
    const s = pptx.addSlide();
    s.background = { color: T.bg };
    s.addShape(pptx.ShapeType.ellipse, { x: W - 4.6, y: -1.6, w: 6.2, h: 6.2, fill: { color: T.accent, transparency: 85 }, line: { type: 'none' } });
    s.addShape(pptx.ShapeType.ellipse, { x: W - 2.9, y: 4.3, w: 4.2, h: 4.2, fill: { color: T.accent2, transparency: 80 }, line: { type: 'none' } });
    s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.35, h: H, fill: { color: T.accent }, line: { type: 'none' } });
    if (B.logo) s.addImage({ data: imgData(B.logo), x: 1.0, y: 0.6, w: 1.6, h: 0.9, sizing: { type: 'contain', w: 1.6, h: 0.9 } });
    s.addText(deck.title, { x: 1.0, y: 1.8, w: 9.8, h: 2.0, fontSize: deck.title.length > 45 ? 36 : 44, bold: true, color: T.title, fontFace: F, valign: 'bottom', margin: 0 });
    s.addShape(pptx.ShapeType.rect, { x: 1.0, y: 3.98, w: 1.4, h: 0.08, fill: { color: T.accent }, line: { type: 'none' } });
    if (deck.subtitle) s.addText(deck.subtitle, { x: 1.0, y: 4.2, w: 9.8, h: 0.9, fontSize: 20, color: T.body, fontFace: F, valign: 'top', margin: 0 });
    if (B.presenter) {
      s.addText(B.presenter, { x: 1.0, y: 5.35, w: 8, h: 0.45, fontSize: 18, bold: true, color: T.title, fontFace: F, margin: 0 });
      if (B.designation) s.addText(B.designation, { x: 1.0, y: 5.8, w: 8, h: 0.4, fontSize: 14, color: T.muted, fontFace: F, margin: 0 });
    }
    const foot = [B.company, B.tagline].filter(Boolean).join('  |  ');
    if (foot) s.addText(foot, { x: 1.0, y: H - 0.75, w: 9, h: 0.4, fontSize: 12, color: T.muted, fontFace: F, margin: 0 });
  }

  function closingSlide(c, deck, num) {
    const { pptx, T, F, B } = c;
    const s = frame(c, num);
    s.addText(THANKS[c.lang] || THANKS.English, { x: 0.6, y: 2.2, w: W - 1.2, h: 1.4, fontSize: 54, bold: true, color: T.title, fontFace: F, align: 'center', valign: 'middle', margin: 0 });
    s.addShape(pptx.ShapeType.rect, { x: W / 2 - 0.8, y: 3.75, w: 1.6, h: 0.08, fill: { color: T.accent }, line: { type: 'none' } });
    const sub = B.presenter ? [B.presenter, B.designation].filter(Boolean).join(', ') : deck.title;
    s.addText(sub, { x: 0.6, y: 4.05, w: W - 1.2, h: 0.6, fontSize: 18, color: T.body, fontFace: F, align: 'center', margin: 0 });
  }

  async function build(deck, o) {
    const pptx = new PptxGenJS();
    pptx.layout = 'LAYOUT_WIDE';
    pptx.title = deck.title;
    const B = o.brand || {};
    pptx.author = B.presenter || 'FreePPTMaker';
    if (B.company) pptx.company = B.company;
    const c = { pptx, T: themeFor(o.theme, B), F: fontFor(o.lang), B, lang: o.lang, chart: o.chart };

    titleSlide(c, deck);
    deck.slides.forEach((d, i) => {
      const s = frame(c, i + 2);
      if (d.type !== 'quote') heading(c, s, d.title);
      (DRAW[d.type] || DRAW.bullets)(c, s, d);
      if (d.notes) s.addNotes(d.notes);
    });
    closingSlide(c, deck, deck.slides.length + 2);
    return pptx;
  }

  window.Render = { build, themeFor, fontFor, onColor, THANKS };
})();
