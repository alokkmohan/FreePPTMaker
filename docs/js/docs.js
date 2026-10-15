// Reads uploaded files in the browser: text from PDF/DOCX/TXT, chart data from CSV/XLSX.
(function () {
  'use strict';

  const MAX_BYTES = 15 * 1024 * 1024;
  const ext = f => (f.name.split('.').pop() || '').toLowerCase();

  async function pdfText(file) {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(await file.arrayBuffer()) }).promise;
    let out = '';
    for (let p = 1; p <= Math.min(pdf.numPages, 60); p++) {
      const page = await pdf.getPage(p);
      const tc = await page.getTextContent();
      out += tc.items.map(i => i.str).join(' ') + '\n';
    }
    return out;
  }

  const num = v => {
    if (typeof v === 'number') return v;
    const n = parseFloat(String(v == null ? '' : v).replace(/[,₹$€£%\s]/g, ''));
    return isNaN(n) ? null : n;
  };

  function toChart(rows, name) {
    rows = (rows || []).filter(r => Array.isArray(r) && r.some(c => String(c == null ? '' : c).trim() !== ''));
    if (rows.length < 2) throw new Error('The data file needs a header row and at least one data row.');
    const header = rows[0].map(h => String(h == null ? '' : h).trim());
    const data = rows.slice(1, 16);
    const numericCols = [];
    for (let j = 1; j < header.length; j++) {
      const vals = data.map(r => num(r[j]));
      if (vals.filter(v => v !== null).length >= Math.ceil(data.length / 2)) numericCols.push(j);
    }
    if (!numericCols.length) throw new Error('No numeric column found. Put labels in the first column and numbers in the next ones.');
    const labels = data.map(r => String(r[0] == null ? '' : r[0]));
    const series = numericCols.slice(0, 4).map(j => ({ name: header[j] || 'Series ' + j, values: data.map(r => num(r[j]) || 0) }));
    const summary = [header.join(', ')].concat(data.map(r => header.map((_, j) => r[j] == null ? '' : r[j]).join(', '))).join('\n').slice(0, 2500);
    return { name, labels, series, summary, chartType: 'bar', title: header[numericCols[0]] || 'Data' };
  }

  window.Docs = {
    isData: f => ['csv', 'xlsx', 'xls'].includes(ext(f)),

    async text(file) {
      if (file.size > MAX_BYTES) throw new Error(file.name + ' is larger than 15 MB.');
      const e = ext(file);
      if (e === 'txt' || e === 'md') return file.text();
      if (e === 'pdf') return pdfText(file);
      if (e === 'docx') return (await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() })).value;
      throw new Error('Unsupported file type: ' + file.name);
    },

    async table(file) {
      if (file.size > MAX_BYTES) throw new Error(file.name + ' is larger than 15 MB.');
      let rows;
      if (ext(file) === 'csv') {
        rows = Papa.parse(await file.text(), { skipEmptyLines: true }).data;
      } else {
        const wb = XLSX.read(await file.arrayBuffer(), { type: 'array' });
        rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, raw: true, blankrows: false });
      }
      return toChart(rows, file.name);
    }
  };
})();
