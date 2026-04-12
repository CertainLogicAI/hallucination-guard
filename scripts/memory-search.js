const fs = require('fs');
const path = require('path');

function memorySearch(query) {
  const memoryDir = path.join(__dirname, '../memory');
  const files = fs.readdirSync(memoryDir);
  const results = [];

  files.forEach(file => {
    try {
      const content = fs.readFileSync(path.join(memoryDir, file), 'utf8');
      const lines = content.split('\n');
      
      lines.forEach((line, index) => {
        if (line.toLowerCase().includes(query.toLowerCase())) {
          results.push({
            file: file,
            line: index + 1,
            snippet: line.trim()
          });
        }
      });
    } catch (err) {
      console.error(`Error reading ${file}:`, err.message);
    }
  });

  return results;
}

// Export for CLI use
if (require.main === module) {
  const query = process.argv[2] || '';
  const results = memorySearch(query);
  
  console.log(`Found ${results.length} results for "${query}":`);
  results.forEach(result => {
    console.log(`\n${result.file}:${result.line}`);
    console.log(`  ${result.snippet}`);
  });
}

module.exports = memorySearch;
