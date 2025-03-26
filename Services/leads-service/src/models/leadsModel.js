const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';

const db = knex(config[env]);

// Criar lead
async function createLead(name, email, score = 0, source = 'unknown') {
  return db('leads').insert({ name, email, score, source }).returning('*');
}

// Listar todos os leads
async function getAllLeads() {
  return db('leads').select('*');
}

// Buscar lead por ID
async function getLeadById(id) {
  return db('leads').where({ id }).first();
}

// Atualizar lead
async function updateLead(id, data) {
  // data pode conter { name, email, score, source }
  return db('leads').where({ id }).update(data).returning('*');
}

// Deletar lead
async function deleteLead(id) {
  return db('leads').where({ id }).del();
}

// Exemplo adicional: busca por email
async function findLeadByEmail(email) {
  return db('leads').where({ email }).first();
}

module.exports = {
  createLead,
  getAllLeads,
  getLeadById,
  updateLead,
  deleteLead,
  findLeadByEmail
};