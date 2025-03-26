// src/types/user.ts

export enum UserRole {
  ADMIN = 'admin',
  AFFILIATE = 'affiliate',
  USER = 'user',
}

export enum UserStatus {
  ACTIVE = 'active',
  PENDING = 'pending',
  SUSPENDED = 'suspended',
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  createdAt?: Date;
  updatedAt?: Date;
}
