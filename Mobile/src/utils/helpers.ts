// src/utils/helper.ts
// Conjunto de funções auxiliares (helpers) para formatação, validação, etc.

export function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

export function formatDate(date: Date): string {
  // Exemplo: converte Date → "DD/MM/YYYY"
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

export function generateRandomId(prefix: string = 'ID'): string {
  // Exemplo: gera ID pseudoaleatório
  const random = Math.floor(Math.random() * 1_000_000);
  return `${prefix}-${Date.now()}-${random}`;
}

// Exemplo de validação simples
export function isEmailValid(email: string): boolean {
  // Regex básico, só como ilustração
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email.toLowerCase());
}

// Crie quantas funções precisar para manipulação de strings, arrays, datas, etc.
