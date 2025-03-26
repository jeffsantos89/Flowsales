import crypto from 'crypto';
import { logger } from '../src/utils/logger';

const ALGORITHM = 'aes-256-cbc';
const IV_LENGTH = 16;

// Validação segura da chave de criptografia
const getEncryptionKey = (): Buffer => {
  const key = process.env.ENCRYPTION_KEY;

  if (!key) {
    logger.error('ENCRYPTION_KEY não configurada.');
    throw new Error('ENCRYPTION_KEY não configurada.');
  }

  if (key.length !== 32) {
    logger.error('ENCRYPTION_KEY inválida. A chave deve conter 32 caracteres.');
    throw new Error('ENCRYPTION_KEY inválida. A chave deve conter 32 caracteres.');
  }

  try {
    return Buffer.from(key, 'utf-8');
  } catch (error) {
    logger.error(`Erro ao criar Buffer da ENCRYPTION_KEY: ${error.message}`);
    throw new Error('Erro ao processar ENCRYPTION_KEY.');
  }
};

export const encrypt = (plainText: string): string => {
  try {
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, getEncryptionKey(), iv);
    const encrypted = Buffer.concat([cipher.update(plainText, 'utf8'), cipher.final()]);

    return `${iv.toString('hex')}:${encrypted.toString('hex')}`;
  } catch (error) {
    logger.error(`Erro ao criptografar texto: ${error.message}`);
    throw new Error('Erro durante a criptografia');
  }
};

export const decrypt = (encryptedText: string): string => {
  try {
    const [ivHex, dataHex] = encryptedText.split(':');

    if (!ivHex || !dataHex) {
      logger.error('Formato inválido do texto criptografado.');
      throw new Error('Formato inválido do texto criptografado.');
    }

    const iv = Buffer.from(ivHex, 'hex');
    const encryptedData = Buffer.from(dataHex, 'hex');
    const decipher = crypto.createDecipheriv(ALGORITHM, getEncryptionKey(), iv);
    const decrypted = Buffer.concat([decipher.update(encryptedData), decipher.final()]);

    return decrypted.toString('utf8');
  } catch (error) {
    logger.error(`Erro ao descriptografar texto: ${error.message}`);
    throw new Error('Erro durante a descriptografia');
  }
};
