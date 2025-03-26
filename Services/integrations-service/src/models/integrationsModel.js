// integrationsModel.js
const knex = require('knex');
const config = require('../../config');
const env = config.env;
const db = knex(require('../../knexfile')[env]);

async function createIntegration(name, description, type) {
  return db('integrations').insert({ name, description, type }).returning('*');
}
module.exports = { createIntegration };
