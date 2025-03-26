const express = require('express');
const router = express.Router();
const logger = require('../logger');
const {
  validateCreateAutomation
} = require('../validations/automationsValidation');
const {
  createEmailAutomation,
  getAllEmailAutomations,
  getEmailAutomationById,
  updateEmailAutomation,
  deleteEmailAutomation
} = require('../models/emailModel');
const { sendEmailNow, scheduleEmail } = require('../helpers/emailSender');

// GET /email-automations
router.get('/', async (req, res, next) => {
  try {
    const automations = await getAllEmailAutomations();
    logger.info(`[GET] Fetched ${automations.length} automations`);
    res.json(automations);
  } catch (error) {
    next(error);
  }
});

// POST /email-automations
router.post('/', validateCreateAutomation, async (req, res, next) => {
  try {
    const { name, description, trigger, action } = req.body;
    const [newAutomation] = await createEmailAutomation(name, description, trigger, action);
    logger.info(`[POST] Created automation: ${newAutomation.name}`);
    res.status(201).json(newAutomation);
  } catch (error) {
    next(error);
  }
});

// GET /email-automations/:id
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const automation = await getEmailAutomationById(id);
    if (!automation) {
      return res.status(404).json({ error: 'Not found' });
    }
    res.json(automation);
  } catch (error) {
    next(error);
  }
});

// PUT /email-automations/:id
router.put('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const data = req.body;
    const [updated] = await updateEmailAutomation(id, data);
    if (!updated) {
      return res.status(404).json({ error: 'Not found' });
    }
    logger.info(`[PUT] Updated automation ID=${id}`);
    res.json(updated);
  } catch (error) {
    next(error);
  }
});

// DELETE /email-automations/:id
router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    await deleteEmailAutomation(id);
    logger.info(`[DELETE] Deleted automation ID=${id}`);
    res.json({ message: 'Deleted' });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /email-automations/:id/send
 * body: { to, subject, text, html }
 * Envia email imediatamente
 */
router.post('/:id/send', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { to, subject, text, html } = req.body;
    const automation = await getEmailAutomationById(id);
    if (!automation) {
      return res.status(404).json({ error: 'Not found' });
    }

    const info = await sendEmailNow({
      from: `"Flowsale" <${process.env.EMAIL_USER}>`,
      to,
      subject: subject || `Ação: ${automation.action}`,
      text: text || `Disparo: ${automation.description}`,
      html: html || `<p>Disparo: ${automation.description}</p>`
    });

    res.json({ message: 'Email sent', messageId: info.messageId });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /email-automations/:id/schedule
 * body: { to, subject, text, html, delayMillis }
 * Agenda o envio (Bull). delayMillis = tempo em ms
 */
router.post('/:id/schedule', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { to, subject, text, html, delayMillis } = req.body;
    if (!delayMillis) {
      return res.status(400).json({ error: 'delayMillis is required' });
    }

    const automation = await getEmailAutomationById(id);
    if (!automation) {
      return res.status(404).json({ error: 'Not found' });
    }

    await scheduleEmail({
      from: `"Flowsale" <${process.env.EMAIL_USER}>`,
      to,
      subject: subject || `Ação: ${automation.action}`,
      text: text || `Disparo: ${automation.description}`,
      html: html || `<p>Disparo: ${automation.description}</p>`,
      delayMillis
    });

    res.json({ message: 'Email scheduled', delayMillis });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
