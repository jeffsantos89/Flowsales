import { affiliateRepository } from '../repositories/affiliateRepository';
import bcrypt from 'bcrypt';
import Joi from 'joi';
import { ApiError } from '../utils/apiError';
import redisClient from '../config/redisConfig';
import logger from '../utils/logger';
import { Affiliate } from '../entities/Affiliate';

// Definição do DTO para o Affiliate
interface AffiliateDTO {
  name: string;
  email: string;
  password: string;
}

// Definição do DTO para a resposta da API
interface AffiliateResponseDTO {
  id: number;
  name: string;
  email: string;
}

// Validação dos dados usando Joi
const affiliateSchema = Joi.object<AffiliateDTO>({
  name: Joi.string().min(3).max(50).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
});

// Cache Key
const AFFILIATE_CACHE_KEY = 'affiliates_cache';

// Criação de um novo Afiliado com validação e criptografia segura
export const createAffiliate = async (
  data: AffiliateDTO
): Promise<AffiliateResponseDTO> => {
  // Valida os dados com Joi
  const { error } = affiliateSchema.validate(data);
  if (error) {
    logger.warn(`Erro de validação ao criar afiliado: ${error.message}`);
    throw new ApiError(400, error.message);
  }

  // Verifica se o email já está cadastrado
  const existingAffiliate = await affiliateRepository.findOneBy({
    email: data.email,
  });
  if (existingAffiliate) {
    logger.warn(`Tentativa de cadastro com email existente: ${data.email}`);
    throw new ApiError(409, 'Email já cadastrado.');
  }

  // Criptografa a senha com mais rounds para segurança
  const saltRounds = 12;
  const hashedPassword = await bcrypt.hash(data.password, saltRounds);

  const affiliate = new Affiliate();
  Object.assign(affiliate, {
    ...data,
    password: hashedPassword,
  });

  const savedAffiliate = (await affiliateRepository.save(
    affiliate
  )) as Affiliate;

  // Limpa o cache após adicionar novo afiliado
  await redisClient.del(AFFILIATE_CACHE_KEY);

  logger.info(`Afiliado criado com sucesso: ${savedAffiliate.email}`);

  return {
    id: Number(savedAffiliate.id),
    name: savedAffiliate.name,
    email: savedAffiliate.email,
  };
};

// Retorna a lista de Afiliados com Cache
export const getAffiliates = async (): Promise<AffiliateResponseDTO[]> => {
  try {
    const cachedAffiliates = await redisClient.get(AFFILIATE_CACHE_KEY);
    if (cachedAffiliates) {
      logger.info('Afiliados carregados do cache.');
      return JSON.parse(cachedAffiliates);
    }

    const affiliates = await affiliateRepository.findAll();

    const affiliateResponses: AffiliateResponseDTO[] = affiliates.map(
      (affiliate: Affiliate) => ({
        id: affiliate.id,
        name: affiliate.name,
        email: affiliate.email,
      })
    );

    await redisClient.setEx(
      AFFILIATE_CACHE_KEY,
      600,
      JSON.stringify(affiliateResponses)
    );

    logger.info('Afiliados carregados do banco e cache atualizado.');
    return affiliateResponses;
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Erro desconhecido';
    logger.error(`Erro ao buscar afiliados: ${errorMessage}`);
    throw new ApiError(500, 'Erro ao buscar afiliados.');
  }
};
