
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