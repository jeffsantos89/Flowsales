const cluster = require('cluster');
const os = require('os');

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`);

  // Cria um worker por CPU disponível
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  // Se um worker morrer, recriamos
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died. Spawning a new one...`);
    cluster.fork();
  });
} else {
  // Cada worker roda o servidor principal
  require('./server');
}
