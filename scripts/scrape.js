// Corpus Coranicum Variants Scraper
const { chromium } = require('playwright');
const fs = require('fs').promises;

// Ayah counts per surah (Hafs numbering)
const AYAH_COUNTS = [
  7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
  123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
  112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
  34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
  54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
  60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
  14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
  28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
  29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
  15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
  11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
  5, 4, 5, 6
];

async function scrapeVariants(surah, verse) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const url = `https://corpuscoranicum.de/en/verse-navigator/sura/${surah}/verse/${verse}/variants`;
  console.log(`Scraping ${surah}:${verse}...`);
  
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Wait for the table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Extract table data
    const data = await page.evaluate(() => {
      const table = document.querySelector('table');
      if (!table) return [];
      
      // Get header to map column indices to word positions
      const headerCells = Array.from(table.querySelectorAll('thead tr:last-child th'));
      const colToWordPos = {};
      headerCells.forEach((th, colIdx) => {
        const id = th.getAttribute('id');
        if (id && id.startsWith('word-column-')) {
          const wordNum = parseInt(id.replace('word-column-', ''));
          colToWordPos[colIdx] = wordNum;
        }
      });
      
      const tbody = table.querySelector('tbody');
      if (!tbody) return [];
      
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const variants = [];
      
      let currentWork = null;
      
      rows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length === 0) return;
        
        const workText = cells[0].textContent.trim();
        
        if (workText.includes('gest.') || workText.includes(':')) {
          currentWork = workText.split('Info')[0].trim();
        }
        
        if (!cells[1]) return;
        
        const readerDivs = cells[1].querySelectorAll('.max-w-sm');
        const readers = Array.from(readerDivs).map(div => {
          const span = div.querySelector('span');
          return span ? span.textContent.trim() : '';
        });
        
        if (readers.length === 0) {
          const directText = cells[1].textContent.trim().split('Info')[0].trim();
          readers.push(directText); // may be empty string for base reading row
        }
        
        // Extract words with positions using column mapping
        const words = {};
        cells.forEach((cell, colIdx) => {
          if (colToWordPos[colIdx]) {
            const word = cell.textContent.trim();
            if (word) {
              words[colToWordPos[colIdx]] = word;
            }
          }
        });
        
        if (Object.keys(words).length > 0) {
          readers.forEach(reader => {
            variants.push({
              work: currentWork,
              reader: reader,
              words: words
            });
          });
        }
      });
      
      return variants;
    });
    
    await browser.close();
    return { surah, verse, variants: data, success: true };
    
  } catch (error) {
    await browser.close();
    return { surah, verse, error: error.message, success: false };
  }
}

async function main() {
  console.log('Scraping all 114 surahs...\n');
  
  const allVariants = [];
  let totalAyahs = 0;
  const TOTAL_EXPECTED = 6236;
  let startTime = Date.now();
  let lastCheckpointTime = Date.now();
  
  for (let surah = 1; surah <= 114; surah++) {
    const ayahCount = AYAH_COUNTS[surah - 1];
    console.log(`\nSurah ${surah} (${ayahCount} ayahs):`);
    
    for (let verse = 1; verse <= ayahCount; verse++) {
      const result = await scrapeVariants(surah, verse);
      
      if (result.success) {
        allVariants.push(result);
        totalAyahs++;
        
        const percent = ((totalAyahs / TOTAL_EXPECTED) * 100).toFixed(2);
        process.stdout.write(`  ${surah}:${verse} - ${result.variants.length} variants [${totalAyahs}/${TOTAL_EXPECTED} = ${percent}%]`);
        
        // Calculate time remaining every 50 verses
        if (totalAyahs % 50 === 0) {
          const now = Date.now();
          const elapsed = (now - lastCheckpointTime) / 1000; // seconds
          const rate = 50 / elapsed; // verses per second
          const remaining = TOTAL_EXPECTED - totalAyahs;
          const timeRemaining = remaining / rate;
          const hours = Math.floor(timeRemaining / 3600);
          const minutes = Math.floor((timeRemaining % 3600) / 60);
          
          console.log(` | ETA: ${hours}h ${minutes}m`);
          
          const outputDir = '../tmp/scraped_variants';
          await fs.mkdir(outputDir, { recursive: true });
          await fs.writeFile(
            `${outputDir}/progress_${totalAyahs}.json`,
            JSON.stringify({ totalAyahs, lastSurah: surah, lastVerse: verse, data: allVariants }, null, 2)
          );
          console.log(`    [Progress saved: ${totalAyahs} ayahs]`);
          
          lastCheckpointTime = now;
        } else {
          console.log('');
        }
      } else {
        console.log(`  ${surah}:${verse} - FAILED: ${result.error}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  const outputDir = '../data';
  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(
    `${outputDir}/all_variants.json`,
    JSON.stringify(allVariants, null, 2)
  );
  
  const totalTime = (Date.now() - startTime) / 1000 / 60; // minutes
  console.log(`\n✓ Scraping complete!`);
  console.log(`Total ayahs scraped: ${totalAyahs} (expected: 6236)`);
  console.log(`Total variants: ${allVariants.reduce((sum, v) => sum + v.variants.length, 0)}`);
  console.log(`Total time: ${Math.floor(totalTime)} minutes`);
  console.log(`Data saved to ${outputDir}/all_variants.json`);
  
  // Run Python fix script
  console.log('\nRunning data quality fixes...');
  const { spawn } = require('child_process');
  const pythonProcess = spawn('python3', ['fix_variants.py']);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(data.toString());
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(data.toString());
  });
  
  pythonProcess.on('close', (code) => {
    if (code === 0) {
      console.log('✓ Data quality fixes applied successfully!');
    } else {
      console.error(`Fix script exited with code ${code}`);
    }
  });
}

main().catch(console.error);
