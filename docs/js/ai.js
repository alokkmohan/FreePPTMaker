// Talks to the Apps Script proxy and turns AI output into a clean deck object.
(function () {
  'use strict';

  const SYSTEM = 'You are an expert presentation writer and designer. You always reply with one valid JSON object and nothing else.';
  const TYPES = ['bullets', 'two_column', 'stats', 'timeline', 'quote', 'chart'];

  async function call(messages) {
    const url = (window.CONFIG || {}).APPS_SCRIPT_URL;
    if (!url) throw new Error('Backend not set up yet: add your Apps Script URL in docs/js/config.js.');
    let res;
    try {
      // No custom headers → "simple" request, so no CORS preflight to Apps Script.
      res = await fetch(url, { method: 'POST', body: JSON.stringify({ messages, json: true }) });
    } catch (e) {
      throw new Error('Could not reach the AI server. Check your internet connection.');
    }
    let data;
    try { data = JSON.parse(await res.text()); }
    catch (e) { throw new Error('Unexpected server response. Is the Apps Script deployed with access "Anyone"?'); }
    if (!data.ok) throw new Error(data.error || 'AI request failed.');
    return data.text;
  }

  function parseJSON(text) {
    const t = String(text || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '');
    const a = t.indexOf('{'), b = t.lastIndexOf('}');
    if (a < 0 || b < a) throw new Error('AI did not return valid JSON.');
    return JSON.parse(t.slice(a, b + 1));
  }

  async function callJSON(messages) {
    try { return parseJSON(await call(messages)); }
    catch (e) {
      if (!/JSON|Unexpected token|position/i.test(e.message)) throw e;
      return parseJSON(await call(messages)); // one retry on malformed JSON
    }
  }

  // ── normalisation ────────────────────────────────────────────────
  const str = (v, max) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, max);
  const list = (v, max, len) => (Array.isArray(v) ? v : []).map(x => str(typeof x === 'object' && x ? (x.text || x.label || '') : x, len)).filter(Boolean).slice(0, max);

  function normSlide(s) {
    s = s && typeof s === 'object' ? s : {};
    const o = {
      type: TYPES.includes(s.type) ? s.type : 'bullets',
      title: str(s.title, 90),
      notes: str(s.notes, 1500),
      image_prompt: str(s.image_prompt, 200)
    };
    const asBullets = items => Object.assign(o, { type: 'bullets', bullets: items.length ? items : [o.title || '—'] });

    switch (o.type) {
      case 'two_column': {
        const col = c => ({ heading: str(c && c.heading, 60), bullets: list(c && c.bullets, 5, 160) });
        o.left = col(s.left); o.right = col(s.right);
        if (!o.left.bullets.length || !o.right.bullets.length) return asBullets(o.left.bullets.concat(o.right.bullets));
        break;
      }
      case 'stats':
        o.stats = (Array.isArray(s.stats) ? s.stats : []).slice(0, 4)
          .map(x => ({ value: str(x && x.value, 12), label: str(x && x.label, 90) })).filter(x => x.value);
        if (o.stats.length < 2) return asBullets(o.stats.map(x => `${x.value} — ${x.label}`));
        break;
      case 'timeline':
        o.steps = (Array.isArray(s.steps) ? s.steps : []).slice(0, 5)
          .map(x => ({ label: str(x && x.label, 30), text: str(x && x.text, 120) })).filter(x => x.label || x.text);
        if (o.steps.length < 2) return asBullets(o.steps.map(x => [x.label, x.text].filter(Boolean).join(': ')));
        break;
      case 'quote':
        o.quote = str(s.quote, 300); o.author = str(s.author, 80);
        if (!o.quote) return asBullets(list(s.bullets, 6, 200));
        break;
      case 'chart':
        o.bullets = list(s.bullets, 4, 160);
        break;
      default:
        asBullets(list(s.bullets, 6, 200));
    }
    return o;
  }

  function normDeck(d, wanted) {
    d = d && typeof d === 'object' ? d : {};
    let slides = (Array.isArray(d.slides) ? d.slides : []).map(normSlide);
    if (!slides.length) throw new Error('AI returned no slides. Please try again.');
    if (wanted && slides.length > wanted + 2) slides = slides.slice(0, wanted);
    return { title: str(d.title, 100) || 'Presentation', subtitle: str(d.subtitle, 140), slides };
  }

  // ── prompts ──────────────────────────────────────────────────────
  const SHAPES = hasChart => `Slide object types:
1. {"type":"bullets","title":"...","bullets":["...","...","...","..."],"image_prompt":"...","notes":"..."}
2. {"type":"two_column","title":"...","left":{"heading":"...","bullets":["...","...","..."]},"right":{"heading":"...","bullets":["...","...","..."]},"notes":"..."}
3. {"type":"stats","title":"...","stats":[{"value":"75%","label":"..."},{"value":"2.5M","label":"..."},{"value":"#1","label":"..."}],"notes":"..."}
4. {"type":"timeline","title":"...","steps":[{"label":"...","text":"..."},{"label":"...","text":"..."},{"label":"...","text":"..."}],"notes":"..."}
5. {"type":"quote","quote":"...","author":"...","notes":"..."}
${hasChart ? '6. {"type":"chart","title":"...","bullets":["...","..."],"notes":"..."}\n' : ''}`;

  const STYLE_RULES = `- Slide titles: max 40 characters.
- Bullets: 3-5 per slide, each one complete, specific sentence of max 16 words. No emojis, no markdown, no numbering.
- Timeline: 3-5 steps; label max 20 characters, text max 12 words. Stats: 3-4 items, value max 8 characters.
- Use "stats" only with real, widely known figures (or figures from the source document). Never invent statistics.
- Use "quote" only with a real, correctly attributed quote.
- "notes": 2-4 sentences the presenter can say for that slide.
- "image_prompt": short English description of a relevant illustration (bullets slides only).`;

  const langRule = lang => `LANGUAGE: ${lang}. Write ALL visible text (titles, bullets, labels, quotes, notes) in ${lang}${lang !== 'English' ? ' using its native script' : ''}. "image_prompt" must always be in English. JSON keys stay in English.`;

  function deckMessages(o) {
    const k = Math.max(1, o.slides - 2);
    const doc = o.docText ? `\nSOURCE DOCUMENT — base the presentation on this content and do not invent facts beyond it:\n"""\n${o.docText}\n"""\n` : '';
    const data = o.chart ? `\nDATA TABLE from the user (a ${o.chart.chartType} chart will be drawn from it):\n${o.chart.summary}\nInclude exactly one slide of type "chart" with a title and 2-3 "bullets" giving insights from this data.\n` : '';
    const user = `Create a presentation as JSON.
TOPIC: ${o.topic || '(derive it from the source document)'}
${langRule(o.lang)}
TONE: ${o.tone || 'Professional'}. AUDIENCE: ${o.audience || 'General audience'}.
${o.extra ? 'EXTRA INSTRUCTIONS: ' + o.extra + '\n' : ''}${doc}${data}
Return exactly this JSON shape:
{"title":"...","subtitle":"...","slides":[ ...exactly ${k} slide objects... ]}

${SHAPES(!!o.chart)}
RULES:
- "slides" must contain exactly ${k} objects. The title slide and thank-you slide are added automatically, so do not include them.
- First slide: introduction/overview (bullets). Last slide: conclusion or key takeaways (bullets).
- Mix layouts for variety: mostly "bullets", plus some "two_column" (comparisons, pros/cons), "timeline" (history, process, steps), at most one "stats" and at most one "quote".
- "title": max 60 characters. "subtitle": max 90 characters.
${STYLE_RULES}
Output only the JSON object.`;
    return [{ role: 'system', content: SYSTEM }, { role: 'user', content: user }];
  }

  function editMessages(deck, index, instruction, o) {
    const slide = Object.assign({}, deck.slides[index]); delete slide.img;
    const around = deck.slides.map((s, i) => `${i + 2}. ${s.title}`).join('\n');
    const user = `You are editing one slide of the presentation "${deck.title}".
${langRule(o.lang)}
All slide titles:
${around}

Current slide ${index + 2} as JSON:
${JSON.stringify(slide)}

USER INSTRUCTION: ${instruction}

Return {"slide": { ...one slide object... }}. You may change the slide type if the instruction asks for it.
${SHAPES(!!o.chart)}
${STYLE_RULES}
Output only the JSON object.`;
    return [{ role: 'system', content: SYSTEM }, { role: 'user', content: user }];
  }

  window.AI = {
    async generateDeck(o) {
      const raw = await callJSON(deckMessages(o));
      const deck = normDeck(raw, Math.max(1, o.slides - 2));
      if (o.chart && !deck.slides.some(s => s.type === 'chart')) {
        deck.slides.splice(Math.max(1, deck.slides.length - 1), 0,
          { type: 'chart', title: o.chart.title || 'Data Overview', bullets: [], notes: '', image_prompt: '' });
      }
      return deck;
    },
    async editSlide(deck, index, instruction, o) {
      const raw = await callJSON(editMessages(deck, index, instruction, o));
      return normSlide(raw && raw.slide ? raw.slide : raw);
    }
  };
})();
