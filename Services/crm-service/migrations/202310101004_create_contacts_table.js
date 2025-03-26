exports.up = function(knex) {
  return knex.schema.createTable('contacts', table => {
    table.increments('id').primary();
    table.string('name').notNullable();
    table.string('email').notNullable().unique();
    table.string('phone', 20);
    table.string('company', 100);
    table.timestamps(true, true);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('contacts');
};