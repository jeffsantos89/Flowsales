require('dotenv').config();
const express = require('express');
const http = require('http');
const socketIO = require('socket.io');

const ssl = require('./ssl'); // para HTTPS, se desejar
const logger = require('./logger');
const { connectARI } = require('./ariClient');
const auth = require('./auth');
const errorHandling = require('./errorHandling');
const sip = require('./sip');
const conference = require('./conference');
const ui = require('./ui');
const callsRoutes = require('./routes/calls');

async function startServer() {
  // Conecta ao Asterisk ARI
  await connectARI(); 

  const app = express();
  app.use(express.json());

  // Exemplo: rota simples de saúde
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', pid: process.pid, date: new Date() });
  });

  // Middleware de autenticação básica (exemplo)
  app.use(auth);

  // Rotas SIP (placeholder)
  app.use('/sip', sip);

  // Rotas de conferência (placeholder)
  app.use('/conference', conference);

  // Rotas de UI (placeholder)
  app.use('/', ui);

  // Rotas de chamadas
  app.use('/calls', callsRoutes);

  // Middleware global de tratamento de erros
  app.use(errorHandling);

  // Se quiser servir via HTTPS, descomente e use “server = https.createServer(...)”.
  // const server = require('https').createServer(ssl.getCredentials(), app);
  const server = http.createServer(app);

  // Socket.io
  const io = socketIO(server);

  io.on('connection', (socket) => {
    logger.info(`Client connected [PID=${process.pid}] via Socket.io`);

    // Exemplo: ao receber "getCalls", podemos retornar lista de chamadas
    socket.on('getCalls', () => {
      // Lógica real: fetch de canais do ARI
      socket.emit('callsList', [
        { channelId: 'abc123', state: 'Up', connectedLineNum: '1001' }
      ]);
    });

    socket.on('disconnect', () => {
      logger.info('Client disconnected from Socket.io');
    });
  });

  const PORT = process.env.PORT || 3009;
  server.listen(PORT, () => {
    logger.info(`VoIP worker (PID: ${process.pid}) running on port ${PORT}`);
  });
}

// Inicia o servidor
startServer().catch(err => {
  logger.error('Error starting server', err);
  process.exit(1);
});
