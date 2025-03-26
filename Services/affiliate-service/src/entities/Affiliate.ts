import {
  BeforeInsert,
  BeforeUpdate,
  Column,
  CreateDateColumn,
  DeleteDateColumn,
  Entity,
  OneToMany,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from 'typeorm';
import { Commission } from './Commission';
import bcrypt from 'bcrypt';

@Entity({ name: 'affiliates' })
export class Affiliate {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ type: 'varchar', length: 255 })
  name!: string;

  @Column({ type: 'varchar', length: 255, unique: true })
  email!: string;

  @Column({ type: 'varchar', length: 255, select: false })
  password!: string;

  @OneToMany(() => Commission, (commission) => commission.affiliate, {
    cascade: true,
  })
  commissions!: Commission[];

  @Column({ type: 'boolean', default: true })
  isActive!: boolean;

  @Column({ type: 'boolean', default: false })
  isDeleted!: boolean;

  @CreateDateColumn({ type: 'timestamp' })
  createdAt!: Date;

  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt!: Date;

  @DeleteDateColumn({ type: 'timestamp', nullable: true })
  deletedAt?: Date;

  @Column()
  firstName!: string;

  @Column()
  lastName!: string;

  @BeforeInsert()
  @BeforeUpdate()
  async normalizeEmail() {
    this.email = this.email.toLowerCase().trim();
  }

  @BeforeInsert()
  async hashPassword() {
    this.password = await bcrypt.hash(this.password, 12);
  }
}
