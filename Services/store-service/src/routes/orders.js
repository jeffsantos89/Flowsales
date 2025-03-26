const jwtAuth = require('../auth');
router.use(jwtAuth);
const express = require('express');
const router = express.Router();
const logger = require('../logger');
const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';
const db = knex(config[env]);

// POST /orders - criar pedido (exemplo simples)
router.post('/', async (req, res) => {
  try {
    // Exemplo: o corpo JSON contém { "session_id": "abc123" }
    // e assumimos que já temos a lista de cart_items
    const { session_id } = req.body;
    if (!session_id) {
      return res.status(400).json({ error: 'session_id é obrigatório' });
    }

    // Buscar itens do carrinho
    const cartItems = await db('cart_items')
      .where({ session_id })
      .select('product_id', 'quantity');

    if (!cartItems || cartItems.length === 0) {
      return res.status(400).json({ error: 'Carrinho está vazio ou não existe' });
    }

    // Obter informações de preço dos produtos
    const productIds = cartItems.map(item => item.product_id);
    const products = await db('products').whereIn('id', productIds);
    
    let total = 0;
    const itemsToInsert = [];

    for (const item of cartItems) {
      const product = products.find(p => p.id === item.product_id);
      if (!product) {
        return res.status(400).json({ error: `Produto não encontrado no ID ${item.product_id}` });
      }
      
      // Calcula subtotal
      const lineTotal = parseFloat(product.price) * item.quantity;
      total += lineTotal;

      // Monta item para inserir em order_items
      itemsToInsert.push({
        product_id: product.id,
        quantity: item.quantity,
        price: product.price // ou lineTotal / item.quantity (depende do que você quer salvar)
      });
    }

    // Cria pedido
    const orderNumber = `ORD-${Date.now()}`;
    const [newOrder] = await db('orders').insert({
      order_number: orderNumber,
      total: total.toFixed(2)
    }).returning('*');

    // Cria order_items
    for (const it of itemsToInsert) {
      await db('order_items').insert({
        order_id: newOrder.id,
        product_id: it.product_id,
        quantity: it.quantity,
        price: it.price
      });
    }

    // Limpa o carrinho (opcional)
    await db('cart_items').where({ session_id }).del();

    logger.info('Pedido criado', { orderId: newOrder.id, orderNumber });
    res.json({
      message: 'Pedido criado com sucesso',
      order: {
        ...newOrder,
        items: itemsToInsert
      }
    });
  } catch (error) {
    logger.error('Erro ao criar pedido', { error });
    res.status(500).json({ error: 'Erro ao criar pedido' });
  }
});

// GET /orders/:id - obter detalhes de um pedido
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const order = await db('orders').where({ id }).first();
    if (!order) {
      return res.status(404).json({ error: 'Pedido não encontrado' });
    }
    const items = await db('order_items').where({ order_id: id });
    res.json({ order, items });
  } catch (error) {
    logger.error('Erro ao obter pedido', { error });
    res.status(500).json({ error: 'Erro ao obter pedido' });
  }
});

// PUT /orders/:id - atualizar status do pedido
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    if (!status) {
      return res.status(400).json({ error: 'status é obrigatório' });
    }
    const [updated] = await db('orders')
      .where({ id })
      .update({ status })
      .returning('*');
    if (!updated) {
      return res.status(404).json({ error: 'Pedido não encontrado para atualizar' });
    }
    logger.info('Pedido atualizado', { orderId: updated.id, status });
    res.json(updated);
  } catch (error) {
    logger.error('Erro ao atualizar pedido', { error });
    res.status(500).json({ error: 'Erro ao atualizar pedido' });
  }
});

// DELETE /orders/:id - cancela o pedido (exemplo simples)
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    // Em um caso real, você pode apenas atualizar o status para "canceled"
    const rowsDeleted = await db('orders').where({ id }).del();
    if (!rowsDeleted) {
      return res.status(404).json({ error: 'Pedido não encontrado para deletar' });
    }
    logger.info('Pedido deletado', { orderId: id });
    // Apagamos itens
    await db('order_items').where({ order_id: id }).del();
    res.json({ message: 'Pedido excluído com sucesso' });
  } catch (error) {
    logger.error('Erro ao excluir pedido', { error });
    res.status(500).json({ error: 'Erro ao excluir pedido' });
  }
});

module.exports = router;