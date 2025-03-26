export type Currency = 'USD' | 'EUR' | 'BRL';

export interface CommissionData {
  date: string;
  total: number;
  currency: Currency;
  status: 'PENDING' | 'PAID' | 'CANCELLED';
  transactionId?: string;
}

export interface AffiliateMetrics {
  active: number;
  inactive: number;
  pending: number;
  total: number;
  growthRate: number; // percentage of growth compared to previous period
}

export interface CommissionMetrics {
  total: number;
  currency: Currency;
  pending: number;
  paid: number;
  averagePerAffiliate: number;
  conversionRate: number; // percentage of successful conversions
}

export interface DashboardResponseDTO {
  affiliateMetrics: AffiliateMetrics;
  commissionMetrics: CommissionMetrics;
  commissionHistory: CommissionData[];
  lastUpdated: string; // ISO date string
  periodStart: string; // ISO date string
  periodEnd: string; // ISO date string
  version: string; // API version
}
