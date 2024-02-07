const express = require('express');
const app = express();

// Middleware para permitir requisições de origens diferentes (CORS)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

// Função para gerar os nós com as cores correspondentes ao fluxo especificado
function generateNodes(flowId) {
  const style = {
    borderRadius: "50%",
    width: "100px",
    height: "100px",
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: "100%",
    fontWeight: 700,
    color: "black",
  };

  let colors;

  // Atribuir cores com base no fluxo especificado
  switch (flowId) {
    case 1:
      colors = ['#198754', '#198754', '#198754', '#198754'];
      break;
    case 2:
      colors = ['#198754', '#198754', '#dc3545', '#ffc107'];
      break;
    case 3:
      colors = ['#198754', '#dc3545', '#ffc107', '#ffc107'];
      break;
    default:
      colors = ['gray', 'gray', 'gray', 'gray'];
      break;
  }

  const labels = ['Order', 'Stock', 'Payment', 'Delivery'];
  const initialNodes = [];

  // Gerar os nós com os nomes atribuídos e cores correspondentes
  for (let i = 0; i < labels.length; i++) {
    const nodeId = (i + 1).toString();
    const node = {
      id: nodeId,
      position: {x: 600 + i * 400, y: 300},
      data: {label: labels[i]}, // Adicionando o atributo oldLabel com o valor original de label
      style: {...style, background: colors[i]},
      type: nodeId === '1' ? 'input' : 'default',
      sourcePosition: 'right',
      targetPosition: 'left'
    };
    initialNodes.push(node);
  }

  return initialNodes;
}

// Rota para retornar os nós com as cores correspondentes ao fluxo especificado
app.get('/nodes/:flowId', (req, res) => {
  const flowId = parseInt(req.params.flowId);
  const nodes = generateNodes(flowId);
  res.json(nodes);
});

// Iniciar o servidor na porta 3000
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
