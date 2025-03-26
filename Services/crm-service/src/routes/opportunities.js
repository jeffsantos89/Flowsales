const express = require('express');
const router = express.Router();
const logger = require('../logger');

// Exemplo: GET /opportunities - lista as oportunidades
router.get('/', (req, res) => {
  // Buscar no BD (por ex.: SELECT * FROM opportunities)
  logger.info('Listando oportunidades (exemplo estático).');
  res.json([
    { id: 1, name: 'Oportunidade 1', stage: 'Proposal', value: 1000 },
    { id: 2, name: 'Oportunidade 2', stage: 'Negotiation', value: 2000 }
  ]);
});

// Exemplo: POST /opportunities - criar oportunidade
router.post('/', (req, res) => {
  logger.info('Criando nova oportunidade (exemplo estático).');
  const { name, stage, value } = req.body;
  // Insert no BD
  res.json({ message: 'Oportunidade criada com sucesso!', name, stage, value });
});

module.exports = router;