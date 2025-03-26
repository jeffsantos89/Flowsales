// src/database/shardManager.ts
import { Pool } from 'pg';
import shards from './shardingConfig';

const pools = shards.map((shard) => ({
  name: shard.name,
  pool: new Pool({
    host: shard.host,
    port: shard.port,
    user: shard.user,
    password: shard.password,
    database: shard.database,
  }),
}));

export const getShard = (userId: string) => {
  const shardIndex = parseInt(userId) % pools.length;
  return pools[shardIndex].pool;
};

export const executeShardQuery = async (userId: string, query: string) => {
  const pool = getShard(userId);
  return pool.query(query);
};
