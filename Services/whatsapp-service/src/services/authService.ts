import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { User } from '../entities/User';
import { AppDataSource } from '../config/db';
import { config } from '../config';

const userRepository = AppDataSource.getRepository(User);

export const authService = {
  register: async (email: string, password: string) => {
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = userRepository.create({ email, password: hashedPassword });
    return await userRepository.save(newUser);
  },

  login: async (email: string, password: string) => {
    const user = await userRepository.findOneBy({ email });
    if (!user) throw new Error('Usuário não encontrado!');

    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) throw new Error('Senha inválida!');

    const token = jwt.sign({ id: user.id, role: user.role }, config.jwtSecret, { expiresIn: '1h' });
    return { token, user };
  },
};
