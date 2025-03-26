import dotenv from 'dotenv';
import logger from '../utils/logger';

dotenv.config();

interface LogstashConfig {
  level?: string;
  host: string;
  port?: number;
  ssl?: boolean;
  maxRetries?: number;
}

const logstashConfig: LogstashConfig = {
  host: process.env.LOGSTASH_HOST || 'localhost',
  port: parseInt(process.env.LOGSTASH_PORT || '5044'),
  level: process.env.LOG_LEVEL || 'info',
  ssl: process.env.LOGSTASH_SSL === 'true',
  maxRetries: parseInt(process.env.LOGSTASH_MAX_RETRIES || '5'),
};

// 🔹 Validações para evitar falhas em produção
if (!logstashConfig.host) {
  throw new Error(
    'LOGSTASH_HOST não foi definido! Verifique suas variáveis de ambiente.'
  );
}
if (!logstashConfig.port || isNaN(logstashConfig.port)) {
  throw new Error(
    'LOGSTASH_PORT inválido! Certifique-se de que é um número válido.'
  );
}

// 🔹 Log para depuração
logger.info(
  `[Logstash] Configuração carregada: ${JSON.stringify(logstashConfig)}`
);

export default logstashConfig;
