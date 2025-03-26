const express = require('express');
const router = express.Router();
const mercadopago = require('mercadopago');
const logger = require('../logger');
const knexConfig = require('../../knexfile');
const knex = require('knex')(knexConfig.development);

mercadopago.configure({
  access_token: process.env.MERCADO_PAGO_ACCESS_TOKEN
});

// Criar pagamento
router.post('/create-payment', async (req, res) => {
  const { productId, amount } = req.body;
  try {
    const preference = {
      items: [
        {
          title: `Produto ${productId}`,
          unit_price: Number(amount),
          quantity: 1
        }
      ],
      back_urls: {
        success: 'http://localhost:3000/success',
        failure: 'http://localhost:3000/failure'
      },
      auto_return: 'approved'
    };

    const response = await mercadopago.preferences.create(preference);

    // Cria registro do pagamento no BD (PENDING)
    await knex('payments').insert({
      product_id: productId,
      amount: Number(amount),
      payment_status: 'PENDING'
    });

    logger.info(`Payment preference created for product ${productId}, amount ${amount}`);
    return res.json({ paymentUrl: response.body.init_point });
  } catch (error) {
    logger.error(error);
    return res.status(500).json({ error: 'Error creating payment' });
  }
});

// Exemplo adicional: rota de atualização ao receber callback do Mercado Pago
router.post('/webhook', async (req, res) => {
  try {
    // Implementar lógica de atualização de status
    // Exemplo: status = req.body.status; paymentId = req.body.id
    logger.info(`Received payment webhook: ${JSON.stringify(req.body)}`);
    return res.sendStatus(200);
  } catch (error) {
    logger.error(error);
    return res.status(500).json({ error: 'Error processing webhook' });
  }
});

module.exports = router;