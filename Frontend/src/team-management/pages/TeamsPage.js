 
import React, { useEffect, useState } from 'react';
import { fetchTeams, addTeam } from '../api/teamManagement';

const TeamsPage = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    const getTeams = async () => {
      try {
        const teamsData = await fetchTeams();
        setTeams(teamsData);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error fetching teams:', error);
      }
    };
    getTeams();
  }, []);

  const handleAddTeam = async () => {
    try {
      const newTeam = await addTeam(name, description);
      setTeams([...teams, newTeam]);
    } catch (error) {
      console.error('Error adding team:', error);
    }
  };

  if (loading) return <div>Loading teams...</div>;

  return (
    <div>
      <h2>Teams Management</h2>
      <ul>
        {teams.map(team => (
          <li key={team.id}>
            <h3>{team.name}</h3>
            <p>{team.description}</p>
          </li>
        ))}
      </ul>
      <h3>Add New Team</h3>
      <input 
        type="text" 
        placeholder="Team Name" 
        value={name} 
        onChange={(e) => setName(e.target.value)} 
      />
      <input 
        type="text" 
        placeholder="Description" 
        value={description} 
        onChange={(e) => setDescription(e.target.value)} 
      />
      <button onClick={handleAddTeam}>Add Team</button>
    </div>
  );
};

export default TeamsPage;
