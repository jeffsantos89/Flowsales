const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';

const db = knex(config[env]);

async function createEmailAutomation(name, description, trigger, action) {
  return db('email_automations').insert({ name, description, trigger, action }).returning('*');
}

async function getAllEmailAutomations() {
  return db('email_automations').select('*').orderBy('id', 'asc');
}

async function getEmailAutomationById(id) {
  return db('email_automations').where({ id }).first();
}

async function updateEmailAutomation(id, data) {
  return db('email_automations').where({ id }).update(data).returning('*');
}

async function deleteEmailAutomation(id) {
  return db('email_automations').where({ id }).del();
}

module.exports = {
  createEmailAutomation,
  getAllEmailAutomations,
  getEmailAutomationById,
  updateEmailAutomation,
  deleteEmailAutomation
};
