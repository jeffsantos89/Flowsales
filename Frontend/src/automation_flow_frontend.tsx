
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';

export default function AutomationFlow() {
  const [flows, setFlows] = useState([]);
  const [newFlow, setNewFlow] = useState({ nome: '', descricao: '', nodes: [], edges: [] });
  const history = useHistory();

  useEffect(() => {
    axios.get('/automacoes')
      .then(res => setFlows(res.data))
      .catch(console.error);
  }, []);

  const createFlow = () => {
    axios.post('/automacoes', newFlow)
      .then(res => {
        setFlows([...flows, res.data]);
        history.push(`/automacoes/${res.data.id}`);
      })
      .catch(console.error);
  };

  const editFlow = (flowId) => {
    history.push(`/automacoes/${flowId}`);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Automação de Fluxos</h2>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Nome da automação"
          className="input"
          value={newFlow.nome}
          onChange={e => setNewFlow({ ...newFlow, nome: e.target.value })}
        />
        <textarea
          placeholder="Descrição"
          className="input"
          value={newFlow.descricao}
          onChange={e => setNewFlow({ ...newFlow, descricao: e.target.value })}
        ></textarea>
        <button onClick={createFlow} className="btn btn-primary mt-2">Criar Automação</button>
      </div>
      <div className="space-y-4">
        {flows.map(flow => (
          <div key={flow.id} className="p-4 border">
            <h3 className="font-bold text-xl">{flow.nome}</h3>
            <p>{flow.descricao}</p>
            <button onClick={() => editFlow(flow.id)} className="btn btn-secondary mt-2">Editar</button>
          </div>
        ))}
      </div>
    </div>
  );
}
    