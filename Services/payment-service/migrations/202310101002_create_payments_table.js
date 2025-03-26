exports.up = function(knex) {
  return knex.schema.createTable('payments', table => {
    table.increments('id').primary();
    table.string('product_id').notNullable();
    table.float('amount').notNullable();
    table.string('payment_status').defaultTo('PENDING');
    table.timestamps(true, true);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('payments');
};