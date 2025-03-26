import { cartRepository } from '../repositories/cartRepository';
import { Product } from '../entities/Product';

export const addProductToCart = async (userId: number, product: Product) => {
  const cart = await cartRepository.findOneBy({ userId });
  cart.products.push(product);
  return await cartRepository.save(cart);
};

export const getCartByUser = async (userId: number) => {
  return await cartRepository.findOneBy({ userId });
};

export const removeProductFromCart = async (userId: number, productId: number) => {
  const cart = await cartRepository.findOneBy({ userId });
  cart.products = cart.products.filter((p) => p.id !== productId);
  return await cartRepository.save(cart);
};

export const clearUserCart = async (userId: number) => {
  const cart = await cartRepository.findOneBy({ userId });
  cart.products = [];
  return await cartRepository.save(cart);
};
