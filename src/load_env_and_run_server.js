#!/usr/bin/env node

/**
 * Script para carregar variáveis de ambiente e iniciar o servidor Airtable
 * Este script lê o arquivo .env e inicia o servidor Airtable usando as 
 * variáveis de ambiente configuradas.
 */

require('dotenv').config();
const { execSync, spawn } = require('child_process');

// Verifica se a chave API está configurada
const apiKey = process.env.AIRTABLE_API_KEY;

if (!apiKey) {
  console.error('❌ Erro: A variável de ambiente AIRTABLE_API_KEY não está configurada');
  console.error('   Copie o arquivo .env.example para .env e configure as variáveis');
  process.exit(1);
}

console.log('✅ Variáveis de ambiente carregadas com sucesso');
console.log('🚀 Iniciando servidor Airtable...');

// Comando para iniciar o servidor Airtable
const config = { airtableApiKey: apiKey };
const configJson = JSON.stringify(config);

try {
  // Usamos spawn para manter o processo em execução
  const server = spawn('npx', [
    '-y',
    '@smithery/cli@latest',
    'run',
    'airtable-server',
    '--config',
    configJson
  ], {
    stdio: 'inherit' // Redireciona stdin/stdout/stderr para o processo pai
  });

  server.on('error', (error) => {
    console.error(`❌ Erro ao iniciar o servidor: ${error.message}`);
    process.exit(1);
  });

  // Passar sinais de término para o processo filho
  process.on('SIGINT', () => {
    server.kill('SIGINT');
  });
  
  process.on('SIGTERM', () => {
    server.kill('SIGTERM');
  });

  // Captura o código de saída do processo filho
  server.on('close', (code) => {
    console.log(`Servidor encerrado com código ${code}`);
    process.exit(code);
  });
} catch (error) {
  console.error(`❌ Erro ao iniciar o servidor: ${error.message}`);
  process.exit(1);
} 