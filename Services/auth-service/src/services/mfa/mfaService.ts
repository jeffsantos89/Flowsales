export const verifyTOTP = (username: string, token: string): boolean => {
  // Aqui seria feita a verificação com base em TOTP real (Google Authenticator)
  return token === "123456";  // mock
};
