const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';

const db = knex(config[env]);

// Cria um pagamento no status PENDING
async function createPayment(productId, amount) {
  return db('payments').insert({
    product_id: productId,
    amount,
    payment_status: 'PENDING'
  }).returning('*'); // retorna registro inserido, se quiser
}

// Atualiza status de pagamento (PENDING, APPROVED, FAILED, etc.)
async function updatePaymentStatus(paymentId, status) {
  return db('payments')
    .where({ id: paymentId })
    .update({ payment_status: status });
}

// Buscar pagamento por ID
async function getPaymentById(paymentId) {
  return db('payments').where({ id: paymentId }).first();
}

module.exports = {
  createPayment,
  updatePaymentStatus,
  getPaymentById
};