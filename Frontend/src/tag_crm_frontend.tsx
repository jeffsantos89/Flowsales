
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function TagsManager() {
  const [tags, setTags] = useState([]);
  const [newTag, setNewTag] = useState({ nome: '', origem: '', lead_ids: [] });
  const [leads, setLeads] = useState([]);

  useEffect(() => {
    axios.get('/tags')
      .then(res => setTags(res.data))
      .catch(console.error);

    axios.get('/leads')
      .then(res => setLeads(res.data))
      .catch(console.error);
  }, []);

  const createTag = () => {
    axios.post('/tags', newTag)
      .then(res => {
        setTags([...tags, res.data]);
        setNewTag({ nome: '', origem: '', lead_ids: [] });
      })
      .catch(console.error);
  };

  const addLeadsToTag = (tagId) => {
    const tag = tags.find(t => t.id === tagId);
    axios.put(`/tags/${tagId}/leads`, { leads: tag.lead_ids })
      .then(res => console.log('Leads vinculados:', res.data))
      .catch(console.error);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Gestão de Tags CRM</h2>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Nome da Tag"
          className="input"
          value={newTag.nome}
          onChange={e => setNewTag({ ...newTag, nome: e.target.value })}
        />
        <input
          type="text"
          placeholder="Origem"
          className="input"
          value={newTag.origem}
          onChange={e => setNewTag({ ...newTag, origem: e.target.value })}
        />
        <select
          multiple
          className="input"
          value={newTag.lead_ids}
          onChange={e => setNewTag({ ...newTag, lead_ids: Array.from(e.target.selectedOptions, option => option.value) })}
        >
          {leads.map((lead, i) => (
            <option key={i} value={lead.id}>{lead.name}</option>
          ))}
        </select>
        <button onClick={createTag} className="btn btn-primary mt-2">Criar Tag</button>
      </div>
      <div className="space-y-4">
        {tags.map(tag => (
          <div key={tag.id} className="p-4 border">
            <h3 className="font-bold text-xl">{tag.nome}</h3>
            <p>{tag.origem}</p>
            <button onClick={() => addLeadsToTag(tag.id)} className="btn btn-secondary mt-2">Vincular Leads</button>
          </div>
        ))}
      </div>
    </div>
  );
}
    