import {
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsString,
  Length,
  Min,
} from 'class-validator';

export class AddCommissionDTO {
  @IsString()
  @IsNotEmpty()
  @Length(3, 50, {
    message: 'Affiliate code must be between 3 and 50 characters',
  })
  readonly affiliateCode: string;

  @IsString()
  @IsNotEmpty()
  @Length(1, 100, {
    message: 'Product name must be between 1 and 100 characters',
  })
  readonly product: string;

  @IsNumber()
  @IsNotEmpty()
  @Min(0, { message: 'Value must be greater than or equal to 0' })
  readonly value: number;

  constructor(affiliateCode: string, product: string, value: number) {
    this.affiliateCode = affiliateCode;
    this.product = product;
    this.value = value;
  }

  @IsOptional()
  @IsString()
  readonly currency?: string = 'USD';

  @IsOptional()
  readonly createdAt: Date = new Date();
}
