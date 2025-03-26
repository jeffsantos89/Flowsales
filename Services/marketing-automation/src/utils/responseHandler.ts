import { Response } from 'express';

const responseHandler = (res: Response, statusCode: number, data: any) => {
  res.status(statusCode).json({ data });
};

export default responseHandler;
