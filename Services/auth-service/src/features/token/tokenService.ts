const usedRefreshTokens: Set<string> = new Set();

export const verifyAndConsumeRefreshToken = (token: string): boolean => {
  if (usedRefreshTokens.has(token)) return false;
  usedRefreshTokens.add(token);
  return true;
};
