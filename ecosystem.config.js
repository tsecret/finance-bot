module.exports = {
  apps : [{
    name: "Finance Bot",
    script: 'bot.py',
    interpreter: 'python3',
    watch: false,
    time: true,
  }],

  deploy : {
    production : {
      user: 'root',
      host: '146.190.239.93',
      key: 'deploy.key',
      ref: 'origin/main',
      repo: 'https://github.com/TSecretT/deutsche-bank-2-google-sheets.git',
      path: '/root/github/deutsche-bank-2-google-sheets',
      'post-deploy': 'pip3 install -r requirements.txt && pm2 reload ecosystem.config.js --env production && pm2 save'
    }
  }
};
