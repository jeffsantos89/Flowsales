// src/database/shardingConfig.ts
export default [
    {
      name: 'shard1',
      host: process.env.SHARD1_HOST || 'localhost',
      port: 5432,
      user: 'postgres',
      password: 'postgres',
      database: 'flowsale_shard1',
    },
    {
      name: 'shard2',
      host: process.env.SHARD2_HOST || 'localhost',
      port: 5432,
      user: 'postgres',
      password: 'postgres',
      database: 'flowsale_shard2',
    },
  ];
  