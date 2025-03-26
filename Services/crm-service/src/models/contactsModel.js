const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';

const db = knex(config[env]);

async function createContact({ name, email, phone, company }) {
  return db('contacts').insert({ name, email, phone, company }).returning('*');
}

async function getAllContacts() {
  return db('contacts').select('*');
}

async function getContactById(id) {
  return db('contacts').where({ id }).first();
}

async function updateContact(id, data) {
  // data pode conter { name, email, phone, company }
  return db('contacts').where({ id }).update(data).returning('*');
}

async function deleteContact(id) {
  return db('contacts').where({ id }).del();
}

module.exports = {
  createContact,
  getAllContacts,
  getContactById,
  updateContact,
  deleteContact
};