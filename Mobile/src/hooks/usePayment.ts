import { useState } from 'react';
import { clearCart } from '../store/slices/cartSlice';
import { validateCard, formatCardNumber, formatExpireDate } from '../utils/cardValidation';
import { PaymentError } from '../utils/errors';
import { paymentApi } from '../services/paymentApi';
import { saveTransaction } from '../services/transactionService';

interface CardInfo {
  cardNumber: string;
  cvv: string;
  expire: string;
  holderName: string;
}

interface CartItem {
  id: string;
  price: number;
  quantity: number;
  productName: string;
}

interface PaymentParams extends CardInfo {
  cartItems: CartItem[];
  totalValue: number;
  setLoading: (loading: boolean) => void;
  dispatch: any;
  navigation: any;
}

export const usePayment = ({
  cardNumber,
  cvv,
  expire,
  holderName,
  cartItems,
  totalValue,
  setLoading,
  dispatch,
  navigation,
}: PaymentParams) => {
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const validatePaymentData = (): boolean => {
    try {
      if (!validateCard({ cardNumber, cvv, expire, holderName })) {
        throw new PaymentError('Dados do cartão inválidos');
      }
      if (cartItems.length === 0 || totalValue <= 0) {
        throw new PaymentError('Carrinho inválido');
      }
      return true;
    } catch (error) {
      setPaymentError(error instanceof PaymentError ? error.message : 'Erro de validação');
      return false;
    }
  };

  const handlePayment = async () => {
    try {
      if (!validatePaymentData()) {
        return;
      }
      setLoading(true);

      // Processar pagamento com API real
      const paymentResult = await paymentApi.processPayment({
        amount: totalValue,
        cardInfo: {
          number: formatCardNumber(cardNumber),
          cvv,
          expire: formatExpireDate(expire),
          holderName,
        },
        items: cartItems,
      });

      if (paymentResult.success && paymentResult.transactionId) {
        // Salvar transação
        await saveTransaction({
          transactionId: paymentResult.transactionId,
          amount: totalValue,
          items: cartItems,
          date: new Date(),
        });

        dispatch(clearCart());
        navigation.navigate('PaymentSuccess', { 
          transactionId: paymentResult.transactionId 
        });
      } else {
        throw new PaymentError(paymentResult.error || 'Erro desconhecido');
      }
    } catch (error) {
      console.error('Payment error:', error);
      if (error instanceof PaymentError) {
        setPaymentError(error.message);
      } else if (error instanceof Error) {
        setPaymentError(error.message);
      } else {
        setPaymentError('Ocorreu um erro no processamento do pagamento');
      }
    } finally {
      setLoading(false);
    }
  };

  return { handlePayment, paymentError };
};

