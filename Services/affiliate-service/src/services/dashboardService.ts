import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { RedisService } from './redisService';
import { ApiError } from '../utils/apiError';
import Logger from '../utils/logger';
import { Affiliate } from '../entities/Affiliate';
import { Commission } from '../entities/Commission';
import { User } from '../types/user';

let commissionRepo: Repository<Commission>;

@Injectable()
export class RepositoryProvider {
  constructor(
    @InjectRepository(Commission)
    commissionRepository: Repository<Commission>
  ) {
    commissionRepo = commissionRepository;
  }
}

// Interfaces
interface IDashboardData {
  totalAffiliates: number;
  totalCommissions: number;
  totalEarnings: number;
}

// Enums
enum CacheKeys {
  DASHBOARD = 'dashboard_data_cache',
}

@Injectable()
export class DashboardService {
  private readonly CACHE_TTL = 300; // 5 minutes in seconds
  constructor(
    @InjectRepository(Affiliate)
    private readonly affiliateRepo: Repository<Affiliate>,

    @InjectRepository(Commission)
    private readonly commissionRepo: Repository<Commission>,

    private readonly cacheService: RedisService,
    private readonly logger: typeof Logger
  ) {
    this.logger = logger;
  }

  public async getDashboardData(): Promise<IDashboardData> {
    try {
      // Verifica se há cache salvo no Redis
      const cachedData = await this.getCachedDashboardData();
      if (cachedData) {
        return cachedData;
      }

      // Caso não haja cache, faz a consulta no banco
      const dashboardData = await this.fetchDashboardData();

      // Salva os dados no cache para futuras requisições
      await this.cacheDashboardData(dashboardData);

      return dashboardData;
    } catch (error) {
      this.handleError(error);
    }
  }

  private async getCachedDashboardData(): Promise<IDashboardData | null> {
    const cachedData = await this.cacheService.get<string>(CacheKeys.DASHBOARD);
    if (cachedData) {
      this.logger.info('Dashboard data loaded from cache');
      return JSON.parse(cachedData);
    }
    return null;
  }

  private async fetchDashboardData(): Promise<IDashboardData> {
    const [totalAffiliates, totalCommissions, totalEarnings] =
      await Promise.all([
        this.affiliateRepo.count(),
        this.commissionRepo.count(),
        this.calculateTotalEarnings(),
      ]);

    return {
      totalAffiliates,
      totalCommissions,
      totalEarnings: totalEarnings || 0,
    };
  }

  private async calculateTotalEarnings(): Promise<number> {
    const result = await this.commissionRepo
      .createQueryBuilder('commission')
      .select('SUM(commission.amount)', 'total')
      .where('commission.status = :status', { status: 'COMPLETED' })
      .getRawOne();

    return result?.total ? parseFloat(result.total) : 0;
  }

  private async cacheDashboardData(data: IDashboardData): Promise<void> {
    await this.cacheService.setEx(
      CacheKeys.DASHBOARD,
      this.CACHE_TTL,
      JSON.stringify(data)
    );
    this.logger.info('Dashboard data cached successfully');
  }

  private handleError(error: unknown): never {
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error';
    this.logger.error(`Error loading dashboard data: ${errorMessage}`);
    throw new ApiError(500, 'Error loading dashboard data');
  }
}

/**
 * Retorna o dashboard específico de um afiliado.
 */
export async function getDashboardData(user: User) {
  try {
    const [sales, revenue, commissions] = await Promise.all([
      fetchUserSales(Number(user.id)),
      calculateUserRevenue(Number(user.id)),
      calculateUserCommissions(Number(user.id)),
    ]);

    return {
      sales,
      revenue,
      commissions,
    };
  } catch (error) {
    Logger.error('Error fetching dashboard data:', error);
    throw new ApiError(500, 'Error fetching dashboard data');
  }
}

/**
 * Obtém o número total de vendas aprovadas de um afiliado.
 */
async function fetchUserSales(userId: number): Promise<number> {
  try {
    const totalSales = await commissionRepo
      .createQueryBuilder('commission')
      .where('commission.affiliateId = :userId', { userId })
      .andWhere('commission.status = :status', { status: 'APPROVED' })
      .getCount();

    return totalSales || 0;
  } catch (error) {
    Logger.error(
      `Erro ao obter total de vendas do usuário ${userId}: ${error}`
    );
    return 0;
  }
}

/**
 * Calcula a receita total gerada pelo afiliado.
 */
async function calculateUserRevenue(userId: number): Promise<number> {
  try {
    const revenueResult = await commissionRepo
      .createQueryBuilder('commission')
      .select('SUM(commission.amount)', 'total')
      .where('commission.affiliateId = :userId', { userId })
      .andWhere('commission.status = :status', { status: 'APPROVED' })
      .getRawOne();

    return revenueResult?.total ? parseFloat(revenueResult.total) : 0;
  } catch (error) {
    Logger.error(`Erro ao calcular receita do afiliado ${userId}: ${error}`);
    return 0;
  }
}

/**
 * Calcula o total de comissões pagas ao afiliado.
 */
async function calculateUserCommissions(userId: number): Promise<number> {
  try {
    const commissionResult = await commissionRepo
      .createQueryBuilder('commission')
      .select('SUM(commission.amount)', 'total')
      .where('commission.affiliateId = :userId', { userId })
      .andWhere('commission.status = :status', { status: 'PAID' })
      .getRawOne();

    return commissionResult?.total ? parseFloat(commissionResult.total) : 0;
  } catch (error) {
    Logger.error(`Erro ao calcular comissões do afiliado ${userId}: ${error}`);
    return 0;
  }
}
