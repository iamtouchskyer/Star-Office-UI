const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

// Load Vercel-style API handlers
const apiHandlers = {
  '/status': require('./api/state'),
  '/api/state': require('./api/state'),
  '/api/health': require('./api/health'),
  '/api/test': require('./api/test'),
  '/api/memo': require('./api/memo'),
  '/api/setstate': require('./api/setstate'),
  '/yesterday-memo': require('./api/yesterday_memo'),
  '/agents': require('./api/agents'),
  '/assets/list': require('./api/assets/list'),
  '/assets/auth/status': require('./api/assets/auth/status'),
};

const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
};

const server = http.createServer((req, rawRes) => {
  const urlObj = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = urlObj.pathname;

  // Check API routes (strip query params already handled by URL)
  const handler = apiHandlers[pathname];
  if (handler) {
    // Simulate Vercel's req/res with minimal shims
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try { req.body = JSON.parse(body); } catch { req.body = {}; }
      req.query = Object.fromEntries(urlObj.searchParams);

      const res = {
        statusCode: 200,
        headers: {},
        status(code) { this.statusCode = code; return this; },
        setHeader(k, v) { this.headers[k] = v; return this; },
        json(data) {
          rawRes.writeHead(this.statusCode, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            ...this.headers,
          });
          rawRes.end(JSON.stringify(data));
        },
        send(data) {
          rawRes.writeHead(this.statusCode, {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin': '*',
            ...this.headers,
          });
          rawRes.end(data);
        },
      };

      try {
        handler(req, res);
      } catch (err) {
        rawRes.writeHead(500, { 'Content-Type': 'application/json' });
        rawRes.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Stub for unimplemented API routes - return sensible defaults
  const apiStubs = {
    '/set_state': { ok: true },
    '/leave-agent': { ok: true },
    '/agent-approve': { ok: true },
    '/agent-reject': { ok: true },
    '/assets/positions': { ok: true, positions: {} },
    '/assets/defaults': { ok: true, defaults: {} },
    '/assets/upload': { ok: true },
    '/assets/restore-default': { ok: true },
    '/assets/restore-prev': { ok: true },
    '/assets/restore-reference-background': { ok: true },
    '/assets/restore-last-generated-background': { ok: true },
    '/assets/generate-rpg-background': { ok: true, task_id: null },
    '/assets/generate-rpg-background/poll': { ok: true, status: 'idle' },
    '/config/gemini': { ok: true, enabled: false },
  };

  if (apiStubs[pathname]) {
    rawRes.writeHead(200, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    });
    rawRes.end(JSON.stringify(apiStubs[pathname]));
    return;
  }

  // Static file serving from public/
  let filePath = path.join(PUBLIC_DIR, pathname === '/' ? 'index.html' : pathname);
  // Strip query string artifacts
  filePath = filePath.split('?')[0];

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Fallback to index.html for SPA-like behavior
      if (!path.extname(pathname)) {
        filePath = path.join(PUBLIC_DIR, 'index.html');
      } else {
        rawRes.writeHead(404);
        rawRes.end('Not found');
        return;
      }
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, data) => {
      if (err) {
        rawRes.writeHead(500);
        rawRes.end('Internal Server Error');
        return;
      }
      rawRes.writeHead(200, { 'Content-Type': contentType });
      rawRes.end(data);
    });
  });
});

server.listen(PORT, () => {
  console.log(`Star Office dev server running at http://localhost:${PORT}`);
});
