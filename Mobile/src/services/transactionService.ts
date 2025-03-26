interface Transaction {
  transactionId: string;
  amount: number;
  items: { id: string; quantity: number; price: number }[];
  date: Date;
}

export const saveTransaction = async (transaction: Transaction): Promise<void> => {
  // Implementar lógica de salvamento da transação aqui
  console.log('Transaction saved:', transaction);
};