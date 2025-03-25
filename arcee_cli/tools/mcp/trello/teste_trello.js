// Script para testar a API do Trello diretamente
const https = require('https');

// Configurações do Trello
const apiKey = '64b83aeb4a38f4f81b5aa69e38c75bec';
const token = 'ATTA990c61c1754403f36cbdd2e90697e8bef99785a0e72af0f3184a97f711472086074DFEF1';
const boardId = 'js3cvo6W';

// URL da API do Trello
const url = `https://api.trello.com/1/boards/${boardId}/lists?key=${apiKey}&token=${token}`;

console.log(`Consultando listas do quadro Trello (ID: ${boardId})...`);
console.log(`URL: ${url}\n`);

// Fazer requisição à API do Trello
https.get(url, (res) => {
  let data = '';
  
  // Receber dados em chunks
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  // Quando terminar de receber dados
  res.on('end', () => {
    console.log(`Status Code: ${res.statusCode}`);
    
    if (res.statusCode === 200) {
      try {
        // Tentar analisar como JSON
        const lists = JSON.parse(data);
        
        console.log(`\nListas no quadro (total: ${lists.length}):`);
        lists.forEach((list, i) => {
          console.log(`${i+1}. ${list.name} (ID: ${list.id})`);
        });
      } catch (e) {
        console.log('Erro ao analisar resposta como JSON:', e.message);
        console.log('Resposta bruta:', data);
      }
    } else {
      console.log(`Erro na requisição: ${res.statusCode}`);
      console.log(`Resposta: ${data}`);
    }
  });
}).on('error', (e) => {
  console.error(`Erro na requisição: ${e.message}`);
}); 