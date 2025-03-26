// logsModel.js
const knex = require('knex');
const config = require('../../config');
const env = config.env;
const db = knex(require('../../knexfile')[env]);

async function createIntegrationLog(integration_type, action, payload, status, error_message) {
  return db('integration_logs').insert({
    integration_type,
    action,
    payload: JSON.stringify(payload),
    status,
    error_message
  });
}
module.exports = { createIntegrationLog };
