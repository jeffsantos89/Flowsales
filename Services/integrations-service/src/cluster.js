const cluster = require('cluster');
const os = require('os');
const logger = require('./logger');
const { startServer } = require('./server');

if (cluster.isMaster) {
  logger.info(`Master ${process.pid} is running`);

  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    logger.error(`Worker ${worker.process.pid} died. Spawning a new one...`);
    cluster.fork();
  });
} else {
  // Worker start
  startServer();
}
