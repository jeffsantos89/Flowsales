export interface CardInfo {
  cardNumber: string;
  cvv: string;
  expire: string;
  holderName: string;
}

export const validateCard = ({ cardNumber, cvv, expire, holderName }: CardInfo): boolean => {
  // Implementar lógica de validação do cartão aqui
  if (!cardNumber || !cvv || !expire || !holderName) {
    return false;
  }
  // Adicionar mais lógica de validação conforme necessário
  return true;
};

export const formatCardNumber = (cardNumber: string): string => {
  // Implementar lógica de formatação do número do cartão aqui
  return cardNumber.replace(/\s+/g, '').replace(/(\d{4})/g, '$1 ').trim();
};

export const formatExpireDate = (expire: string): string => {
  // Implementar lógica de formatação da data de expiração aqui
  return expire.replace(/(\d{2})(\d{2})/, '$1/$2');
};