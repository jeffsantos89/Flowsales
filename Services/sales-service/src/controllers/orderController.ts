import { Request, Response } from 'express';
import { createOrder, getOrders } from '../services/orderService';
import { successResponse, errorResponse } from '../utils/responseHandler';

export const addOrder = async (req: Request, res: Response) => {
  try {
    const order = await createOrder(req.body);
    return successResponse(res, order, 'Order created successfully');
  } catch (error) {
    return errorResponse(res, 'Failed to create order');
  }
};
