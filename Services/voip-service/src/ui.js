const express = require('express');
const path = require('path');
const router = express.Router();

// GET /
// Serve um arquivo HTML estático (placeholder).
router.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'), function(err) {
    if (err) {
      res.send(`<h1>VoIP Service UI</h1>
                <p>Página /index.html não encontrada (placeholder)</p>`);
    }
  });
});

// GET /ui
router.get('/ui', (req, res) => {
  const html = `
  <html>
    <head><title>VoIP Service UI</title></head>
    <body>
      <h1>Bem-vindo ao VoIP Service UI!</h1>
      <p>Aqui você poderia renderizar botões de Ligar, Desligar, Conferência, etc.</p>
    </body>
  </html>`;
  res.send(html);
});

module.exports = router;
