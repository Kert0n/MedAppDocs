// SVG → PNG через тот же Chromium, что у mermaid-cli: шрифты берутся из системы.
const path = require('path');
const puppeteer = require(process.env.PUPPETEER);
(async () => {
  const [src, out, scale] = process.argv.slice(2);
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(src));
  const box = await page.evaluate(() => {
    const r = document.documentElement.getBoundingClientRect();
    return { w: Math.ceil(r.width), h: Math.ceil(r.height) };
  });
  await page.setViewport({ width: box.w, height: box.h, deviceScaleFactor: Number(scale || 2) });
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: box.w, height: box.h } });
  await browser.close();
})();
