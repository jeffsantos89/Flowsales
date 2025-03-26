exports.up = function(knex) {
  return knex.schema.createTable('email_automations', table => {
    table.increments('id').primary();
    table.string('name').notNullable();
    table.string('description').notNullable();
    table.string('trigger').notNullable();
    table.string('action').notNullable();
    table.timestamps(true, true);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('email_automations');
};
