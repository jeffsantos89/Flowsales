import { AppDataSource } from '../config/database';
import { Affiliate } from '../entities/Affiliate';
import { Repository } from 'typeorm';

class AffiliateRepository {
  clear: unknown;
  findAll: unknown;
  async findOneBy(criteria: { email: string }): Promise<Affiliate | null> {
    return await this.repository.findOneBy(criteria);
  }
  private repository: Repository<Affiliate>;

  constructor() {
    this.repository = AppDataSource.getRepository(Affiliate);
  }

  // Criar um novo afiliado
  async createAffiliate(affiliateData: Partial<Affiliate>): Promise<Affiliate> {
    const affiliate = this.repository.create(affiliateData);
    return await this.repository.save(affiliate);
  }

  // Buscar um afiliado por ID
  async getAffiliateById(id: string): Promise<Affiliate | null> {
    return await this.repository.findOne({
      where: { id },
      relations: ['commissions'], // Se precisar carregar comissões relacionadas
    });
  }

  // Buscar todos os afiliados
  async getAllAffiliates(): Promise<Affiliate[]> {
    return await this.repository.find();
  }

  // Atualizar um afiliado
  async updateAffiliate(
    id: number,
    affiliateData: Partial<Affiliate>
  ): Promise<Affiliate | null> {
    await this.repository.update(id, affiliateData);
    return await this.getAffiliateById(id.toString());
  }

  // Deletar um afiliado
  async deleteAffiliate(id: number): Promise<void> {
    await this.repository.delete(id);
  }

  // Salvar um afiliado
  async save(
    affiliate: Partial<Affiliate> | Partial<Affiliate>[]
  ): Promise<Partial<Affiliate> | Partial<Affiliate>[]> {
    if (Array.isArray(affiliate)) {
      return await this.repository.save(affiliate);
    }
    const result = await this.repository.save([affiliate]);
    return result[0];
  }
}

export const affiliateRepository = new AffiliateRepository();
