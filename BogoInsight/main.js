const http = require('http');
const httpProxy = require('http-proxy');
const WebSocket = require('ws');

// 创建 HTTP 代理服务器
const proxy = httpProxy.createProxyServer({ target: 'http://0.0.0.0:8501' });

const server = http.createServer((req, res) => {
    proxy.web(req, res);
});

server.on('request', (req, res) => {
    console.log(`Received request for ${req.url} with method ${req.method}`);
});

server.on('upgrade', (req, socket, head) => {
    proxy.ws(req, socket, head);
});

// 监听代理的关闭事件
proxy.on('close', (req, socket, head) => {
    console.log('Client disconnected');
});

proxy.on('error', (error, req, res) => {
    console.error('Proxy error:', error);
});

server.listen(8000);

// 创建 WebSocket 代理服务器
// const wss = new WebSocket.Server({ server });

// wss.on('connection', (ws, req) => {
//     const target = new WebSocket(`ws://0.0.0.0:8501${req.url}`);
//     ws.on('message', message => target.send(message));
//     target.on('message', message => ws.send(message));
//     ws.on('close', () => target.close());
//     target.on('close', () => ws.close());
// });