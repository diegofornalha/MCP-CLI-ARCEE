#!/usr/bin/env node

/**
 * Script para testar a criação de tarefas no Airtable usando o MCP diretamente.
 */

const { execSync } = require('child_process');
require('dotenv').config();

// Configuração do Airtable a partir de variáveis de ambiente
const base_id = process.env.AIRTABLE_BASE_ID;
const table_id = process.env.AIRTABLE_TABLE_ID;
const apiKey = process.env.AIRTABLE_API_KEY;

// Verifica se as variáveis de ambiente estão configuradas
if (!apiKey || !base_id || !table_id) {
  console.error("❌ Erro: Variáveis de ambiente AIRTABLE_API_KEY, AIRTABLE_BASE_ID e AIRTABLE_TABLE_ID não configuradas.");
  console.error("   Copie o arquivo .env.example para .env e configure as variáveis.");
  process.exit(1);
}

// Dados da tarefa
const taskData = {
  Nome: "Tarefa de teste via NPX",
  Descrição: "Esta tarefa foi criada diretamente pelo NPX",
  Status: "Pendente",
  "Data de Vencimento": new Date().toISOString().split('T')[0],
  Prioridade: "Média"
};

// Comando para criar a tarefa
const command = `npx -y @smithery/cli@latest run airtable-server --config '{"airtableApiKey":"${apiKey}"}' -- create_record --parameters '{"base_id":"${base_id}","table_id":"${table_id}","fields":${JSON.stringify(taskData)}}'`;

console.log("Criando tarefa no Airtable...");
console.log(`Base: ${base_id}, Tabela: ${table_id}`);
console.log(`Dados: ${JSON.stringify(taskData, null, 2)}`);

try {
  const output = execSync(command, { encoding: 'utf8' });
  console.log("Resultado:");
  console.log(output);
  console.log("Tarefa criada com sucesso!");
} catch (error) {
  console.error("Erro ao criar tarefa:");
  console.error(error.message);
  
  if (error.stdout) {
    console.log("Saída padrão:");
    console.log(error.stdout);
  }
  
  if (error.stderr) {
    console.log("Saída de erro:");
    console.log(error.stderr);
  }
}