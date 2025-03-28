import { Lead } from '../entities/Lead';

export interface LeadRepository {
  save(lead: Lead): Promise<void>;
  findByEmail(email: string): Promise<Lead | null>;
}
