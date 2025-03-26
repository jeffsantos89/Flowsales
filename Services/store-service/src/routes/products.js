const express = require('express');
const router = express.Router();
const logger = require('../logger');
const knex = require('knex');
const cfg = require('../../config');
const env = cfg.env;
const db = knex(require('../../knexfile')[env]);
const { createProductSchema } = require('../validations/productValidation');

// GET /products
router.get('/', async (req, res) => {
  try {
    const products = await db('products').select('*');
    res.json(products);
  } catch (error) {
    logger.error('Erro ao listar produtos', { error });
    res.status(500).json({ error: 'Erro ao listar produtos' });
  }
});

// POST /products
router.post('/', async (req, res) => {
  try {
    const { error, value } = createProductSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }
    const [newProduct] = await db('products').insert(value).returning('*');
    logger.info('Produto criado', { productId: newProduct.id });
    res.json(newProduct);
  } catch (error) {
    logger.error('Erro ao criar produto', { error });
    res.status(500).json({ error: 'Erro ao criar produto' });
  }
});

// ... PUT, GET by ID, DELETE, etc.

module.exports = router;
