const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak } = require('docx');

/**
 * Hindi Script to Word Document Converter
 * 
 * यह program Hindi TTS script को professional Word document में convert करता है
 * 
 * Usage:
 * 1. अपनी script file को 'input_script.txt' नाम से इसी folder में रखें
 * 2. Terminal में command run करें: node index.js
 * 3. Output file 'output_document.docx' बन जाएगी
 */

// Configuration - यहाँ settings change कर सकते हैं
const CONFIG = {
    inputFile: 'input_script.txt',      // Input script file का नाम
    outputFile: 'output_document.docx',  // Output Word file का नाम
    
    // Colors
    titleColor: 'FF6F00',        // Title का color (Orange)
    subtitleColor: '1565C0',     // Subtitle का color (Blue)
    headingColor: '1565C0',      // Section headings का color (Blue)
    endQuoteColor: 'D84315',     // End quote का color (Red-Orange)
    
    // Sizes (in half-points, so 24 = 12pt)
    titleSize: 52,               // Title font size
    subtitleSize: 32,            // Subtitle font size
    headingSize: 32,             // Section heading size
    bodySize: 24,                // Normal text size
    
    // Spacing
    paragraphSpacing: 140,       // Paragraph के बाद spacing
};

// Main function
function convertScriptToWord() {
    try {
        console.log('📖 Reading input file...');
        
        // Check if input file exists
        if (!fs.existsSync(CONFIG.inputFile)) {
            console.error(`❌ Error: Input file '${CONFIG.inputFile}' not found!`);
            console.log(`💡 Tip: अपनी script को '${CONFIG.inputFile}' नाम से save करें`);
            return;
        }
        
        // Read the script
        const content = fs.readFileSync(CONFIG.inputFile, 'utf-8');
        const lines = content.split('\n');
        
        console.log('✍️  Processing script...');
        
        const paragraphs = [];
        let skipHeader = true;
        let sectionCount = 0;
        
        // Process each line
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Skip header until we find "Text-to-Speech"
            if (skipHeader) {
                if (line.includes('Text-to-Speech')) {
                    skipHeader = false;
                }
                continue;
            }
            
            // Skip empty lines and markers
            if (!line || line === '[समाप्त]') continue;
            
            // Section headers (=== भाग ===)
            if (line.startsWith('===') && line.includes('भाग')) {
                sectionCount++;
                
                // Add page break before each new section (except first)
                if (paragraphs.length > 3) {
                    paragraphs.push(new Paragraph({ children: [new PageBreak()] }));
                }
                
                const heading = line.replace(/===/g, '').trim();
                paragraphs.push(
                    new Paragraph({
                        heading: HeadingLevel.HEADING_1,
                        spacing: { before: 360, after: 240 },
                        children: [
                            new TextRun({ 
                                text: heading, 
                                bold: true, 
                                size: CONFIG.headingSize, 
                                color: CONFIG.headingColor 
                            })
                        ]
                    })
                );
                continue;
            }
            
            // Regular paragraphs - simple, clean
            paragraphs.push(
                new Paragraph({
                    spacing: { after: CONFIG.paragraphSpacing },
                    children: [new TextRun({ text: line, size: CONFIG.bodySize })]
                })
            );
        }
        
        console.log(`✅ Processed ${sectionCount} sections`);
        console.log('📝 Creating title page...');
        
        // Extract title and subtitle from first few lines
        const firstLines = content.split('\n').slice(0, 5);
        let titleText = 'Hindi Script';
        let subtitleText = 'TTS Document';
        
        for (const line of firstLines) {
            const trimmed = line.trim();
            if (trimmed && !trimmed.includes('Text-to-Speech')) {
                if (titleText === 'Hindi Script') {
                    titleText = trimmed.split(':')[0].trim();
                } else if (subtitleText === 'TTS Document') {
                    if (trimmed.startsWith('(') && trimmed.endsWith(')')) {
                        subtitleText = trimmed.slice(1, -1);
                    } else if (!trimmed.startsWith('===')) {
                        subtitleText = trimmed;
                    }
                    break;
                }
            }
        }
        
        // Create title page
        const titleParagraphs = [
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 240, after: 120 },
                children: [
                    new TextRun({ 
                        text: titleText, 
                        bold: true, 
                        size: CONFIG.titleSize, 
                        color: CONFIG.titleColor 
                    })
                ]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 120 },
                children: [
                    new TextRun({ 
                        text: subtitleText, 
                        bold: true, 
                        size: CONFIG.subtitleSize, 
                        color: CONFIG.subtitleColor 
                    })
                ]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 480 },
                children: [
                    new TextRun({ 
                        text: "Text-to-Speech स्क्रिप्ट", 
                        size: 24, 
                        color: "757575" 
                    })
                ]
            })
        ];
        
        // Add ending page
        paragraphs.push(
            new Paragraph({ children: [new PageBreak()] }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 480, after: 240 },
                children: [
                    new TextRun({ 
                        text: "समाप्त", 
                        bold: true, 
                        size: 48, 
                        color: "2E7D32" 
                    })
                ]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 120 },
                children: [
                    new TextRun({ 
                        text: '"धन्यवाद!"', 
                        italics: true, 
                        size: 32, 
                        color: CONFIG.endQuoteColor 
                    })
                ]
            })
        );
        
        // Combine all paragraphs
        const allParagraphs = [...titleParagraphs, ...paragraphs];
        
        console.log('🎨 Creating Word document...');
        
        // Create document
        const doc = new Document({
            styles: {
                default: {
                    document: {
                        run: { font: "Arial", size: CONFIG.bodySize }
                    }
                },
                paragraphStyles: [
                    {
                        id: "Heading1",
                        name: "Heading 1",
                        basedOn: "Normal",
                        run: { 
                            size: CONFIG.headingSize, 
                            bold: true, 
                            color: CONFIG.headingColor, 
                            font: "Arial" 
                        },
                        paragraph: { spacing: { before: 360, after: 240 } }
                    }
                ]
            },
            sections: [{
                properties: {
                    page: {
                        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                    }
                },
                children: allParagraphs
            }]
        });
        
        // Save document
        console.log('💾 Saving document...');
        Packer.toBuffer(doc).then(buffer => {
            fs.writeFileSync(CONFIG.outputFile, buffer);
            console.log('');
            console.log('✅ SUCCESS!');
            console.log(`📄 Document created: ${CONFIG.outputFile}`);
            console.log(`📊 Total paragraphs: ${allParagraphs.length}`);
            console.log(`📑 Total sections: ${sectionCount}`);
            console.log('');
            console.log('🎉 अब आप Word document को open कर सकते हैं!');
        }).catch(error => {
            console.error('❌ Error saving document:', error.message);
        });
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log('');
        console.log('💡 Troubleshooting tips:');
        console.log('1. Check if input file exists');
        console.log('2. Make sure file is UTF-8 encoded');
        console.log('3. Run: npm install');
    }
}

// Run the converter
console.log('');
console.log('═══════════════════════════════════════');
console.log('  Hindi Script to Word Converter');
console.log('═══════════════════════════════════════');
console.log('');

convertScriptToWord();
