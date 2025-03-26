const jwtAuth = require('../auth');
router.use(jwtAuth);
const express = require('express');
const router = express.Router();
const logger = require('../logger');
const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';
const db = knex(config[env]);

// GET /cart - listar itens do carrinho para uma session_id
router.get('/', async (req, res) => {
  try {
    const { session_id } = req.query;
    if (!session_id) {
      return res.status(400).json({ error: 'session_id é obrigatório' });
    }
    const items = await db('cart_items')
      .where({ session_id })
      .select('*');
    res.json(items);
  } catch (error) {
    logger.error('Erro ao listar carrinho', { error });
    res.status(500).json({ error: 'Erro ao listar carrinho' });
  }
});

// POST /cart - adicionar item ao carrinho
router.post('/', async (req, res) => {
  try {
    const { product_id, quantity, session_id } = req.body;
    if (!product_id || !quantity || !session_id) {
      return res.status(400).json({ error: 'product_id, quantity e session_id são obrigatórios' });
    }
    const [item] = await db('cart_items')
      .insert({ product_id, quantity, session_id })
      .returning('*');
    logger.info('Item adicionado ao carrinho', { cartItemId: item.id });
    res.json(item);
  } catch (error) {
    logger.error('Erro ao adicionar item no carrinho', { error });
    res.status(500).json({ error: 'Erro ao adicionar item no carrinho' });
  }
});

// PUT /cart/:id - atualizar quantidade de um item
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { quantity } = req.body;
    const [updatedItem] = await db('cart_items')
      .where({ id })
            .update({ quantity })
            .returning('*');
          logger.info('Quantidade do item atualizada', { cartItemId: updatedItem.id });
          res.json(updatedItem);
        } catch (error) {
          logger.error('Erro ao atualizar quantidade do item', { error });
          res.status(500).json({ error: 'Erro ao atualizar quantidade do item' });
        }
      });