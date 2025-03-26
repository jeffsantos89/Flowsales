import { AppDataSource } from '../config/database';
import { Commission } from '../entities/Commission';
import {
  DeepPartial,
  EntityRepository,
  Repository,
  SaveOptions,
} from 'typeorm';

@EntityRepository(Commission)
class CommissionRepository extends Repository<Commission> {
  private repository: Repository<Commission>;

  constructor() {
    super(Commission, AppDataSource.manager);
    this.repository = AppDataSource.getRepository(Commission);
  }

  async count(): Promise<number> {
    return await this.repository.count();
  }

  createQueryBuilder(alias: string) {
    return this.repository.createQueryBuilder(alias);
  }

  // Criar uma nova comissão
  create(): Commission;
  create(entityLikeArray: DeepPartial<Commission>[]): Commission[];
  create(entityLike: DeepPartial<Commission>): Commission;
  create(
    commissionData?: DeepPartial<Commission> | DeepPartial<Commission>[]
  ): Commission | Commission[] {
    // Adicione o método 'create'
    if (Array.isArray(commissionData)) {
      return this.repository.create(commissionData);
    }
    return this.repository.create(commissionData || {});
  }

  async save<T extends DeepPartial<Commission>>(
    entity: T,
    options?: SaveOptions
  ): Promise<T> {
    return await this.repository.save(entity, options);
  }

  // Buscar uma comissão por ID
  async getCommissionById(id: number): Promise<Commission | null> {
    return await this.repository.findOne({
      where: { id: String(id) },
      relations: ['affiliate'], // Se precisar carregar afiliado relacionado
    });
  }

  // Buscar todas as comissões
  async getAllCommissions(): Promise<Commission[]> {
    return await this.repository.find({ relations: ['affiliate'] });
  }

  // Atualizar uma comissão
  async updateCommission(
    id: number,
    commissionData: Partial<Commission>
  ): Promise<Commission | null> {
    await this.repository.update(id, commissionData);
    return await this.getCommissionById(id);
  }

  // Deletar uma comissão
  async deleteCommission(id: number): Promise<void> {
    await this.repository.delete(id);
  }
}

export const commissionRepository = new CommissionRepository();
