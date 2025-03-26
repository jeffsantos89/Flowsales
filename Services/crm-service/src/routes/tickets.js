const express = require('express');
const router = express.Router();
const logger = require('../logger');

// GET /tickets - listar tickets
router.get('/', (req, res) => {
  logger.info('Listando tickets (exemplo estático).');
  res.json([
    { id: 101, subject: 'Bug no sistema', status: 'Open' },
    { id: 102, subject: 'Cliente reclamou de X', status: 'Waiting' }
  ]);
});

// POST /tickets - criar ticket
router.post('/', (req, res) => {
  logger.info('Criando novo ticket (exemplo estático).');
  const { subject, status } = req.body;
  // Insert no BD
  res.json({ message: 'Ticket criado com sucesso!', subject, status });
});

module.exports = router;