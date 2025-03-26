const cfg = require('./config');

module.exports = {
  development: {
    client: 'pg',
    connection: {
      host: cfg.db.host,
      user: cfg.db.user,
      password: cfg.db.password,
      database: cfg.db.database,
      port: cfg.db.port
    },
    migrations: {
      directory: './migrations'
    }
  }
};
