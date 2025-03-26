import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne } from 'typeorm';
import { Affiliate } from '../../affiliate-service/src/entities/Affiliate';

@Entity()
export class Order {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  amount: number;

  @Column()
  status: string;

  @ManyToOne(() => Affiliate, (affiliate) => affiliate.id)
  affiliate: Affiliate;

  @CreateDateColumn()
  createdAt: Date;
}
