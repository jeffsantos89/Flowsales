export const successResponse = (res: any, data: any, message = 'Success') => {
    res.status(200).json({
      status: 'success',
      message,
      data,
    });
  };
  
  export const errorResponse = (res: any, message = 'Error', status = 500) => {
    res.status(status).json({
      status: 'error',
      message,
    });
  };
  