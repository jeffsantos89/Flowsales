exports.up = function(knex) {
    return knex.schema.createTable('integrations', table => {
      table.increments('id').primary();
      table.string('name').notNullable();
      table.string('description').notNullable();
      table.string('type').notNullable(); // "social" ou "sms" etc.
      table.timestamps(true, true);
    });
  };
  
  exports.down = function(knex) {
    return knex.schema.dropTable('integrations');
  };
  