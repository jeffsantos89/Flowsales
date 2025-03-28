import jwt from 'jsonwebtoken';
import { verifyTOTP } from '../../services/mfa/mfaService';
import { analyzeLoginPattern } from '../../openai/providers/analyzeLogin';

export const authenticateWithMFA = async (username, password, mfaToken) => {
  // Simulando validação real
  if (username === 'admin' && password === 'admin') {
    const isValidTOTP = verifyTOTP(username, mfaToken);
    if (!isValidTOTP) throw new Error("MFA inválido");

    const analysis = await analyzeLoginPattern({ username });
    if (analysis?.suspicious) throw new Error("Login suspeito (IA)");

    const token = jwt.sign({ username, role: 'admin' }, process.env.JWT_SECRET, { expiresIn: '1h' });
    return { token };
  }
  throw new Error("Credenciais inválidas");
};
