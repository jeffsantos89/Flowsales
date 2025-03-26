import Joi from 'joi';

// Custom Error Classes para tipos específicos de erros
export class ValidationError extends Error {
  /**
   * Represents additional information or data.
   * The type of the details is unknown, and it can be any type.
   */
  details: Joi.ValidationErrorItem[] | undefined;

  constructor({
    message,
    details,
  }: {
    message: string;
    details?: Joi.ValidationErrorItem[];
  }) {
    super(message);
    this.name = 'ValidationError';
    this.details = details;
  }
}

export class DatabaseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DatabaseError';
  }
}

// Interfaces para tipagem forte (TypeScript)
interface AffiliateInput {
  name: string;
  email: string;
  password: string;
}

interface CommissionInput {
  amount: number;
  status: string;
  affiliateId: number;
}

// Schemas Joi para validação avançada
const affiliateSchema = Joi.object({
  name: Joi.string().min(3).max(50).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
});

const commissionSchema = Joi.object({
  amount: Joi.number().positive().required(),
  status: Joi.string().valid('pending', 'approved', 'rejected').required(),
  affiliateId: Joi.number().integer().positive().required(),
});

// Função para validar input de afiliado com Joi
export function validateAffiliateInput(data: AffiliateInput): void {
  const { error } = affiliateSchema.validate(data, { abortEarly: false });
  if (error) {
    throw new ValidationError({
      message: 'Erro de validação de afiliado',
      details: error.details,
    });
  }
}

// Função para validar input de comissão com Joi
export function validateCommissionInput(input: CommissionInput): void {
  const { error } = commissionSchema.validate(input, { abortEarly: false });
  if (error) {
    throw new ValidationError({
      message: 'Erro de validação de comissão',
      details: error.details,
    });
  }
}
