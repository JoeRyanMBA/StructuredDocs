const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push({type: 'pageerror', message: e.message}));
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push({type: 'console', message: msg.text()});
  });
  try {
    await page.goto('http://127.0.0.1:4175/');
    // Navigate to review route (sample token)
    await page.evaluate(() => location.href = '/review/TEST-TOKEN');
    await page.waitForTimeout(800);
    // Wait for #app and look for quill editor root
    const hasEditor = await page.$('.ql-editor');
    console.log('hasEditor=', !!hasEditor);
    // capture errors
    console.log('errors=', JSON.stringify(errors.slice(0,20)));
  } catch (e) {
    console.error('smoke error', e);
  } finally {
    await browser.close();
  }
})();
