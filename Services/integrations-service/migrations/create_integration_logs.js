exports.up = function(knex) {
    return knex.schema.createTable('integration_logs', table => {
      table.increments('id').primary();
      table.string('integration_type').notNullable();
      table.string('action').notNullable();
      table.json('payload');
      table.string('status').notNullable();
      table.text('error_message');
      table.timestamps(true, true);
    });
  };
  
  exports.down = function(knex) {
    return knex.schema.dropTable('integration_logs');
  };
  