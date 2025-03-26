import { Request, Response } from 'express';
import { addProductToCart, getCartByUser, removeProductFromCart, clearUserCart } from '../services/cartService';

export const addToCart = async (req: Request, res: Response) => {
  try {
    const cart = await addProductToCart(req.user.id, req.body);
    res.status(200).json(cart);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getCart = async (req: Request, res: Response) => {
  try {
    const cart = await getCartByUser(req.user.id);
    res.status(200).json(cart);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const removeFromCart = async (req: Request, res: Response) => {
  try {
    await removeProductFromCart(req.user.id, parseInt(req.params.productId));
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const clearCart = async (req: Request, res: Response) => {
  try {
    await clearUserCart(req.user.id);
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
