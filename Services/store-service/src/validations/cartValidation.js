const Joi = require('joi');

exports.createProductSchema = Joi.object({
  name: Joi.string().min(2).required(),
  price: Joi.number().min(0).required(),
  stock: Joi.number().min(0).required()
});
const { createProductSchema } = require('../validations/productValidation');
const express = require('express');
const router = express.Router();

router.post('/', async (req, res) => {
  const { error, value } = createProductSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.details[0].message });
  }
  // value é o body validado
});
// Add your additional routes or middleware here
module.exports = router;