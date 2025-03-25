// Script para listar as listas de um quadro Trello usando MCP.run
const { spawn } = require('child_process');

// Configurações 
const TRELLO_TOKEN = 'ATTA990c61c1754403f36cbdd2e90697e8bef99785a0e72af0f3184a97f711472086074DFEF1';
const TRELLO_BOARD_ID = 'js3cvo6W';
const MCP_SESSION = 'mcpx/diegofornalha/szuUQ5DpbKxQqw8dHtyJR4VzigtpebrB.dAvoQb5AKtEPUl+bZ12fcTg6ov0ZpcBWA2t/jZXNuKY';

// Parâmetros para o Trello
const params = JSON.stringify({
  token: TRELLO_TOKEN,
  board_id: TRELLO_BOARD_ID
});

// Comando para executar o MCP
const cmd = 'mcpx';
const args = [
  'run',
  'trello.board_get_lists',
  '--json', params,
  '--session', MCP_SESSION
];

console.log(`Executando: ${cmd} ${args.join(' ')}`);

// Executar o comando
const mcpProcess = spawn(cmd, args);

// Capturar saída
mcpProcess.stdout.on('data', (data) => {
  console.log(`Resultado:\n${data}`);
  
  // Tentar analisar como JSON se possível
  try {
    const jsonData = JSON.parse(data);
    console.log('\nListas encontradas:');
    if (Array.isArray(jsonData)) {
      jsonData.forEach((lista, index) => {
        console.log(`${index + 1}. ${lista.name} (ID: ${lista.id})`);
      });
    }
  } catch (e) {
    // Se não for JSON, apenas mostra o resultado bruto
  }
});

// Capturar erros
mcpProcess.stderr.on('data', (data) => {
  console.error(`Erro: ${data}`);
});

// Finalização
mcpProcess.on('close', (code) => {
  console.log(`Processo encerrado com código: ${code}`);
}); 