import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, ManyToMany, JoinTable } from 'typeorm';
import { User } from './User';
import { Product } from './Product';

@Entity()
export class Cart {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToOne(() => User, (user) => user.carts)
  user: User;

  @ManyToMany(() => Product)
  @JoinTable()
  products: Product[];
}
