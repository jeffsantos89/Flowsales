import express from 'express';
import metricsRoute from './routes/metricsRoute';
import { authMiddleware } from './middleware/authMiddleware';
import { rateLimiter } from './middleware/rateLimiterMiddleware';

const app = express();
app.use(express.json());
app.use(rateLimiter);
app.use(authMiddleware);
app.use('/api/metrics', metricsRoute);

export default app;
import express from 'express';
import { sendEmail } from './integrations/emailIntegration';
import { sendSms } from './integrations/smsIntegration';
import { sendCrmWebhook } from './integrations/crmWebhook';

const app = express();
app.use(express.json());

app.post('/api/send-email', async (req, res) => {
  const { to, subject, html } = req.body;
  await sendEmail(to, subject, html);
  res.send('Email sent');
});

app.post('/api/send-sms', async (req, res) => {
  const { phoneNumber, message } = req.body;
  await sendSms(phoneNumber, message);
  res.send('SMS sent');
});

app.post('/api/send-crm-webhook', async (req, res) => {
  const { event, data } = req.body;
  await sendCrmWebhook(event, data);
  res.send('CRM Webhook sent');
});

export default app;
import express from 'express';
import swaggerRoute from './routes/swaggerRoute';
import { getLeads } from './services/leadService';

const app = express();
app.use(express.json());
app.use('/api', swaggerRoute);

app.get('/api/leads', async (req, res) => {
  const leads = await getLeads();
  res.json(leads);
});

export default app;
import express from 'express';
import swaggerRoute from './routes/swaggerRoute';
import { executeQuery } from './security/failoverService';
import { runScanner } from './security/vulnerabilityScanner';

const app = express();
app.use(express.json());
app.use('/api', swaggerRoute);

app.get('/api/health', async (req, res) => {
  const result = await executeQuery('SELECT 1');
  res.json({ status: 'OK', db: result ? 'connected' : 'disconnected' });
});

app.get('/api/run-scan', (req, res) => {
  runScanner();
  res.send('Security scan initiated.');
});

export default app;
import express from 'express';
import { getContacts, createContact } from './integrations/crmIntegration';
import { sendTransactionalEmail } from './integrations/emailIntegration';

const app = express();
app.use(express.json());

app.get('/api/contacts', async (_req, res) => {
  const contacts = await getContacts();
  res.json(contacts);
});

app.post('/api/contacts', async (req, res) => {
  const contact = await createContact(req.body);
  res.json(contact);
});

app.post('/api/send-email', async (req, res) => {
  const { to, subject, html } = req.body;
  await sendTransactionalEmail(to, subject, html);
  res.send('Email sent');
});

export default app;
import express from 'express';
import { getFromCache, saveToCache } from './performance/cacheService';
import { optimizeQuery } from './performance/queryOptimizer';
import { runBackup } from './backup/backupService';

const app = express();
app.use(express.json());

app.get('/api/backup', (_req, res) => {
  runBackup();
  res.send('Backup iniciado.');
});

app.get('/api/optimize', async (_req, res) => {
  const report = await optimizeQuery('SELECT * FROM leads');
  res.json(report);
});

export default app;
import express from 'express';
import { securityHeaders } from './security/securityPolicies';

const app = express();
app.use(securityHeaders);
app.use(express.json());

app.get('/api/secure-data', (_req, res) => {
  res.json({ message: 'Secure data access granted' });
});

export default app;
import express from 'express';
import { logInfo, logError } from './logs/logService';
import { getCache, setCache } from './cache/redisClusterService';
import { advancedRateLimiter } from './performance/rateLimiter';

const app = express();
app.use(advancedRateLimiter);
app.use(express.json());

app.get('/api/status', async (req, res) => {
  const cached = await getCache('status');
  if (cached) {
    logInfo('Cache hit for /api/status');
    return res.json(cached);
  }
  const status = { status: 'OK', uptime: process.uptime() };
  await setCache('status', status);
  logInfo('Cache miss for /api/status');
  res.json(status);
});

export default app;
import express from 'express';
import { apiKeyMiddleware } from './security/apiKeyMiddleware';
import { apiKeyRateLimiter } from './performance/rateLimiter';
import { logInfo } from './logs/logService';

const app = express();
app.use(apiKeyMiddleware);
app.use(apiKeyRateLimiter);
app.use(express.json());

app.get('/api/status', (_req, res) => {
  logInfo('Status endpoint accessed');
  res.json({ status: 'OK' });
});

export default app;
