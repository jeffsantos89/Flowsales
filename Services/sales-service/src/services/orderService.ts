import { orderRepository } from '../repositories/orderRepository';

export const createOrder = async (data: any) => {
  const order = orderRepository.create(data);
  return await orderRepository.save(order);
};

export const getOrders = async () => {
  return await orderRepository.find();
};
