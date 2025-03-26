exports.up = function(knex) {
  return knex.schema.createTable('leads', table => {
    table.increments('id').primary();
    table.string('name', 100).notNullable();
    table.string('email').notNullable().unique();
    table.integer('score').defaultTo(0);
    table.string('source', 50).defaultTo('unknown'); // ex.: “website”, “facebook”, etc.
    table.timestamps(true, true);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('leads');
};