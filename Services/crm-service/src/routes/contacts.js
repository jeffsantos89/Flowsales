const express = require('express');
const router = express.Router();
const logger = require('../logger');
const {
  createContact,
  getAllContacts,
  getContactById,
  updateContact,
  deleteContact
} = require('../models/contactsModel');

// POST /contacts - criar contato
router.post('/', async (req, res) => {
  try {
    const { name, email, phone, company } = req.body;
    const [newContact] = await createContact({ name, email, phone, company });
    logger.info(`Novo contato criado => ID=${newContact.id}, email=${newContact.email}`);
    res.json(newContact);
  } catch (error) {
    logger.error('Erro ao criar contato', error);
    res.status(500).json({ error: 'Erro ao criar contato' });
  }
});

// GET /contacts - listar todos
router.get('/', async (req, res) => {
  try {
    const contacts = await getAllContacts();
    res.json(contacts);
  } catch (error) {
    logger.error('Erro ao listar contatos', error);
    res.status(500).json({ error: 'Erro ao listar contatos' });
  }
});

// GET /contacts/:id - obter contato por ID
router.get('/:id', async (req, res) => {
  try {
    const contact = await getContactById(req.params.id);
    if (!contact) {
      return res.status(404).json({ error: 'Contato não encontrado' });
    }
    res.json(contact);
  } catch (error) {
    logger.error('Erro ao buscar contato', error);
    res.status(500).json({ error: 'Erro ao buscar contato' });
  }
});

// PUT /contacts/:id - atualizar contato
router.put('/:id', async (req, res) => {
  try {
    const { name, email, phone, company } = req.body;
    const [updated] = await updateContact(req.params.id, { name, email, phone, company });
    if (!updated) {
      return res.status(404).json({ error: 'Contato não encontrado para atualizar' });
    }
    logger.info(`Contato atualizado => ID=${updated.id}`);
    res.json(updated);
  } catch (error) {
    logger.error('Erro ao atualizar contato', error);
    res.status(500).json({ error: 'Erro ao atualizar contato' });
  }
});

// DELETE /contacts/:id - remover contato
router.delete('/:id', async (req, res) => {
  try {
    const rowsDeleted = await deleteContact(req.params.id);
    if (!rowsDeleted) {
      return res.status(404).json({ error: 'Contato não encontrado para deletar' });
    }
    logger.info(`Contato deletado => ID=${req.params.id}`);
    res.json({ message: 'Contato deletado com sucesso' });
  } catch (error) {
    logger.error('Erro ao deletar contato', error);
    res.status(500).json({ error: 'Erro ao deletar contato' });
  }
});

module.exports = router;