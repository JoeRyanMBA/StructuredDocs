const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const smokeLog = [];

  // Listen for all console events and push them to the log
  page.on('console', msg => {
      const msgText = msg.text();
      console.log(`smoke console: ${msgText}`);
      smokeLog.push(msgText);
  });

  try {
    // Mock the API response before navigating
    await page.route('**/api/review/TEST-TOKEN', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          review: {
            topic_title: 'Smoke Test Topic',
            topic_id: 123,
            due_date: '2025-12-31T23:59:59Z',
            priority: 'high',
            author_message: 'This is a message from the author for the smoke test.',
            topic_content: '<h1>Test Content</h1><p>This is a paragraph for the smoke test.</p>'
          },
          token_info: {
            access_count: 1,
            max_access_count: 10
          },
          feedback_items: []
        }),
      });
    });

    await page.route('**/api/notifications', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.goto('http://127.0.0.1:4175/review/TEST-TOKEN', { waitUntil: 'networkidle' });

    console.log('smoke: Waited for network idle. Checking for editor...');
    // Wait for the Quill editor to be visible
    await page.waitForSelector('.ql-editor', { timeout: 10000 });
    console.log('smoke: Editor found.');

    const hasEditor = await page.locator('.ql-editor').isVisible();
    
    console.log(`smoke: Test passed, hasEditor=${hasEditor}`);
  } catch (error) {
    console.error('smoke error', error);
    // Take a screenshot on error
    await page.screenshot({ path: 'smoke-test-failure.png', fullPage: true });
    console.log('smoke: Screenshot taken.');
    process.exit(1);
  } finally {
    await browser.close();
    // Write smoke log to file
    // fs.writeFileSync('smoke.log', smokeLog.join('\n'));
  }
})();
