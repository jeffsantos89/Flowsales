import { commissionRepository } from '../repositories/commissionRepository';
import Joi from 'joi';
import { ApiError } from '../utils/apiError';
import redisClient from '../config/redisConfig';
import logger from '../utils/logger';

import { CommissionStatus } from '../entities/Commission';

// Definição do DTO para a Commission
interface CommissionDTO {
  amount: number;
  status: CommissionStatus;
  affiliateId: string;
}
const commissionSchema = Joi.object<CommissionDTO>({
  amount: Joi.number().positive().required(),
  status: Joi.string().valid('PENDING', 'PAID', 'REJECTED').required(),
  affiliateId: Joi.number().positive().required(),
});

// Cache Key
const COMMISSION_CACHE_KEY = 'commissions_cache';

// Criação de uma nova Comissão com validação
export const createCommission = async (data: CommissionDTO) => {
  // Valida os dados com Joi
  const { error } = commissionSchema.validate(data);
  if (error) {
    logger.warn(`Erro de validação ao criar comissão: ${error.message}`);
    throw new ApiError(400, error.message);
  }

  try {
    // Cria a comissão
    const commission = commissionRepository.create(data);
    const savedCommission = await commissionRepository.save(commission);

    // Limpa o cache após adicionar nova comissão
    await redisClient.del(COMMISSION_CACHE_KEY);

    logger.info(
      `Comissão criada com sucesso: ${JSON.stringify(savedCommission)}`
    );
    return savedCommission;
  } catch (err: unknown) {
    const errorMessage =
      err instanceof Error ? err.message : 'Erro desconhecido';
    logger.error(`Erro ao salvar comissão: ${errorMessage}`);
    throw new ApiError(500, 'Erro ao salvar comissão.');
  }
};

// Retorna a lista de Comissões com Cache
export const getCommissions = async () => {
  try {
    // Tenta buscar no cache
    const cachedCommissions = await redisClient.get(COMMISSION_CACHE_KEY);
    if (cachedCommissions) {
      logger.info('Comissões carregadas do cache.');
      return JSON.parse(cachedCommissions);
    }

    // Busca no banco se não estiver em cache
    const commissions = await commissionRepository.find();

    // Salva no cache com expiração de 10 minutos
    await redisClient.setEx(
      COMMISSION_CACHE_KEY,
      600,
      JSON.stringify(commissions)
    );

    logger.info('Comissões carregadas do banco e cache atualizado.');
    return commissions;
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Erro desconhecido';
    logger.error(`Erro ao buscar comissões: ${errorMessage}`);
    throw new ApiError(500, 'Erro ao buscar comissões.');
  }
};
