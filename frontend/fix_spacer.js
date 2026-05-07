const fs = require('fs');

const replaceInFile = (file) => {
  let content = fs.readFileSync(file, 'utf8');

  // Find the exact isEmptySpacer function
  const regex = /isEmptySpacer\s*\([^\)]*\)\s*\{[\s\S]*?(?:return false)\n\s*\}/m;
  
  const replacement = `isEmptySpacer(node) {
    if (!node) return false
    
    // Quick out for text nodes with no non-whitespace characters
    if (node.nodeType === Node.TEXT_NODE) {
      if (!node.textContent) return true
      return node.textContent.replace(/[\\s\\u200B-\\u200D\\uFEFF\\u00A0]+/g, '') === ''
    }
    
    if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.tagName === 'BR') return true
      
      // For block-level and inline spacers, check their content
      if (['P', 'DIV', 'SPAN'].includes(node.tagName) || node.tagName === 'LI') {
        const textContent = (node.textContent || '').replace(/[\\s\\u200B-\\u200D\\uFEFF\\u00A0]+/g, '')
        
        // If there's real text, it's not a spacer
        if (textContent.length > 0) return false
        
        // Check for meaningful media or structural elements
        const mediaNodes = node.querySelectorAll('img, video, audio, iframe, canvas, object, hr, table, input, button')
        if (mediaNodes.length > 0) return false
        
        // We only care if it might be an un-merged list or contain one. 
        // If it's a P/DIV that contains a real UL, it shouldn't be skipped.
        const lists = node.querySelectorAll('ul, ol')
        for (let i = 0; i < lists.length; i++) {
          if (lists[i].textContent.replace(/[\\s\\u200B-\\u200D\\uFEFF\\u00A0]+/g, '').length > 0) {
            return false // Contains a list with actual text!
          }
        }
        
        return true
      }
    }
    
    return false
  }`;

  // In htmlToMarkdown it might be `const isEmptySpacer = (node) => {`
  const isHtml = file.includes('htmlToMarkdown');
  const finalReplacement = isHtml ? `const isEmptySpacer = (node) => {\n` + replacement.replace(/^isEmptySpacer\(node\) \{/m, '') : replacement;

  content = content.replace(regex, finalReplacement);
  fs.writeFileSync(file, content);
  console.log('Fixed', file);
}

replaceInFile('src/utils/htmlToMarkdown.js');
replaceInFile('src/components/RichTextEditor.vue');
