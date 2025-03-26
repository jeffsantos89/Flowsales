import { Payment } from '../entities/Payment';
import { paymentRepository } from '../repositories/paymentRepository';

export const processPayment = async (paymentData: Partial<Payment>) => {
  const payment = paymentRepository.create(paymentData);
  return await paymentRepository.save(payment);
};

export const confirmPaymentStatus = async (paymentId: number) => {
  const payment = await paymentRepository.findOneBy({ id: paymentId });
  if (payment) {
    payment.status = 'completed';
    return await paymentRepository.save(payment);
  }
  throw new Error('Payment not found');
};
import Stripe from 'stripe';
import { paymentConfig } from '../config';

const stripe = new Stripe(paymentConfig.apiKey, { apiVersion: '2022-11-15' });

export const processPayment = async (amount: number, token: string) => {
  const paymentIntent = await stripe.paymentIntents.create({
    amount: amount * 100,
    currency: 'usd',
    payment_method: token,
    confirm: true,
  });
  return paymentIntent;
};