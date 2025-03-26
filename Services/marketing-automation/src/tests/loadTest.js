// src/tests/loadTest.js
const { spawn } = require('child_process');

const runLoadTest = () => {
  const artillery = spawn('npx', ['artillery', 'quick', '--count', '50', '--num', '20', 'http://localhost:3000/api/leads']);

  artillery.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  artillery.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  artillery.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
};

runLoadTest();
