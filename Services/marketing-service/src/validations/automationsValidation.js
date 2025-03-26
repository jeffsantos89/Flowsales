const Joi = require('joi');

const createAutomationSchema = Joi.object({
  name: Joi.string().min(3).max(100).required(),
  description: Joi.string().min(5).required(),
  trigger: Joi.string().min(3).required(),
  action: Joi.string().min(3).required()
});

function validateCreateAutomation(req, res, next) {
  const { error } = createAutomationSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.details[0].message });
  }
  next();
}

module.exports = {
  validateCreateAutomation
};
