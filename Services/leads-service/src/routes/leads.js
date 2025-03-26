const express = require('express');
const router = express.Router();
const logger = require('../logger');
const {
  createLead,
  getAllLeads,
  getLeadById,
  updateLead,
  deleteLead,
  findLeadByEmail
} = require('../models/leadsModel');

// POST /leads - criar lead
router.post('/', async (req, res) => {
  try {
    const { name, email, score, source } = req.body;

    // Verifica se já existe um lead com esse email
    const existing = await findLeadByEmail(email);
    if (existing) {
      return res.status(400).json({ error: 'Lead já existe com esse email' });
    }

    const [newLead] = await createLead(name, email, score, source);
    logger.info(`Lead criado: ID=${newLead.id}, email=${newLead.email}`);
    res.json(newLead);
  } catch (error) {
    logger.error('Erro ao criar lead', { error });
    res.status(500).json({ error: 'Erro ao criar lead' });
  }
});

// GET /leads - listar todos os leads
router.get('/', async (req, res) => {
  try {
    const leads = await getAllLeads();
    res.json(leads);
  } catch (error) {
    logger.error('Erro ao listar leads', { error });
    res.status(500).json({ error: 'Erro ao listar leads' });
  }
});

// GET /leads/:id - buscar lead por ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const lead = await getLeadById(id);
    if (!lead) {
      return res.status(404).json({ error: 'Lead não encontrado' });
    }
    res.json(lead);
  } catch (error) {
    logger.error('Erro ao buscar lead por ID', { error });
    res.status(500).json({ error: 'Erro ao buscar lead' });
  }
});

// PUT /leads/:id - atualizar lead
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, email, score, source } = req.body;
    const [updated] = await updateLead(id, { name, email, score, source });
    if (!updated) {
      return res.status(404).json({ error: 'Lead não encontrado para atualizar' });
    }
    logger.info(`Lead atualizado: ID=${updated.id}`);
    res.json(updated);
  } catch (error) {
    logger.error('Erro ao atualizar lead', { error });
    res.status(500).json({ error: 'Erro ao atualizar lead' });
  }
});

// DELETE /leads/:id - deletar lead
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const rowsDeleted = await deleteLead(id);
    if (!rowsDeleted) {
      return res.status(404).json({ error: 'Lead não encontrado para deletar' });
    }
    logger.info(`Lead deletado: ID=${id}`);
    res.json({ message: 'Lead deletado com sucesso' });
  } catch (error) {
    logger.error('Erro ao deletar lead', { error });
    res.status(500).json({ error: 'Erro ao deletar lead' });
  }
});

module.exports = router;