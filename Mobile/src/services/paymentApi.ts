interface PaymentRequest {
  amount: number;
  cardInfo: {
    number: string;
    cvv: string;
    expire: string;
    holderName: string;
  };
  items: { id: string; quantity: number; price: number }[];
}

interface PaymentResponse {
  success: boolean;
  transactionId?: string;
  error?: string;
}

export const paymentApi = {
  processPayment: async (paymentRequest: PaymentRequest): Promise<PaymentResponse> => {
    // Simulate an API call
    return new Promise((resolve) => {
      setTimeout(() => {
        if (Math.random() > 0.5) {
          resolve({
            success: true,
            transactionId: '1234567890',
          });
        } else {
          resolve({
            success: false,
            error: 'Payment failed',
          });
        }
      }, 2000);
    });
  },
};