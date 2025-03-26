const knex = require('knex');
const config = require('../../knexfile');
const env = process.env.NODE_ENV || 'development';

const db = knex(config[env]);

async function createUser(name, email, hashedPassword) {
  return db('users').insert({ name, email, password: hashedPassword });
}

async function findUserByEmail(email) {
  return db('users').where({ email }).first();
}

module.exports = {
  createUser,
  findUserByEmail
};
