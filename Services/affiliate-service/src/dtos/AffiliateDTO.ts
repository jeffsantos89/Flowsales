export interface BaseAffiliateDTO {
  readonly id?: string;
  readonly createdAt?: Date;
  readonly updatedAt?: Date;
  readonly isActive?: boolean;
}

export interface CreateAffiliateDTO extends BaseAffiliateDTO {
  name: string;
  email: string;
  code: string;
  document?: string; // CPF/CNPJ
  phone?: string;
  bankAccount?: {
    bank: string;
    agency: string;
    account: string;
    type: 'checking' | 'savings';
  };
  commissionRate?: number;
  website?: string;
  status?: 'pending' | 'active' | 'suspended' | 'inactive';
  address?: {
    street: string;
    number: string;
    complement?: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
}

export type UpdateAffiliateDTO = Partial<CreateAffiliateDTO>;

export interface AffiliateResponseDTO extends Required<CreateAffiliateDTO> {
  totalSales: number;
  totalCommission: number;
}
