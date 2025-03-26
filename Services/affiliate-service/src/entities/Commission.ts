import {
  BeforeInsert,
  BeforeUpdate,
  Column,
  CreateDateColumn,
  Entity,
  Index,
  ManyToOne,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from 'typeorm';
import { Affiliate } from './Affiliate';

export enum CommissionStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid',
}

@Entity({ name: 'commissions' })
export class Commission {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ type: 'decimal', precision: 15, scale: 2 }) // Maior precisão para valores elevados
  amount!: number;

  @Index()
  @Column({
    type: 'enum',
    enum: CommissionStatus,
    default: CommissionStatus.PENDING,
  })
  status!: CommissionStatus;

  @Column({ type: 'varchar', length: 255, nullable: true })
  description?: string;

  @ManyToOne(() => Affiliate, (affiliate) => affiliate.commissions, {
    eager: false,
    onDelete: 'CASCADE',
  })
  affiliate!: Affiliate;

  @Index()
  @Column({ type: 'uuid' })
  affiliateId!: string;

  @CreateDateColumn({ type: 'timestamp' })
  createdAt!: Date;

  @Column({ type: 'timestamp', nullable: true })
  paidAt?: Date;

  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt!: Date;

  /**
   * 🔹 Valida o status antes de salvar no banco de dados.
   */
  @BeforeInsert()
  @BeforeUpdate()
  protected validateStatus() {
    if (!Object.values(CommissionStatus).includes(this.status)) {
      throw new Error(`Invalid status: ${this.status}`);
    }
  }

  /**
   * 🔹 Método para criar uma comissão com validação.
   */
  static createCommission(
    affiliateId: string,
    amount: number,
    description?: string
  ): Commission {
    if (amount <= 0) {
      throw new Error('Amount must be greater than zero');
    }

    const commission = new Commission();
    commission.affiliateId = affiliateId;
    commission.amount = amount;
    commission.status = CommissionStatus.PENDING;
    commission.description = description;

    return commission;
  }

  /**
   * 🔹 Método para atualizar o status da comissão de forma segura.
   */
  updateStatus(newStatus: CommissionStatus) {
    if (!Object.values(CommissionStatus).includes(newStatus)) {
      throw new Error(`Invalid commission status: ${newStatus}`);
    }

    this.status = newStatus;

    if (newStatus === CommissionStatus.PAID) {
      this.paidAt = new Date();
    }
  }
}
