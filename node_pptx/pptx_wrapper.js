// pptx_wrapper.js - Executes AI-generated PptxGenJS slide code
// Usage: node pptx_wrapper.js <output.pptx> <slides.js>

const PptxGenJS = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

const outputPath = process.argv[2];
const slideCodePath = process.argv[3];

if (!outputPath || !slideCodePath) {
    process.stderr.write(JSON.stringify({ error: "Usage: node pptx_wrapper.js <output.pptx> <slides.js>" }));
    process.exit(1);
}

async function main() {
    try {
        const pptx = new PptxGenJS();
        pptx.layout = 'LAYOUT_WIDE';
        pptx.author = 'AI PPT Generator';

        // Read AI-generated slide code
        const slideCode = fs.readFileSync(slideCodePath, 'utf8');

        // Execute with only pptx in scope (sandboxed)
        const slideFunction = new Function('pptx', slideCode);
        slideFunction(pptx);

        // Resolve output path to absolute
        const absOutput = path.resolve(outputPath);

        // Write PPTX file
        await pptx.writeFile({ fileName: absOutput });

        process.stdout.write(JSON.stringify({ success: true, path: absOutput }));
    } catch (err) {
        process.stderr.write(JSON.stringify({ error: err.message, stack: err.stack }));
        process.exit(1);
    }
}

main();
