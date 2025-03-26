import { Router } from 'express';
import { addToCart, getCart, removeFromCart, clearCart } from '../controllers/cartController';

const router = Router();

router.post('/', addToCart);
router.get('/', getCart);
router.delete('/:productId', removeFromCart);
router.delete('/', clearCart);

export default router;
