 
import { useEffect, useState } from 'react';
import { fetchTeams } from '../api/teamManagement';

const useFetchTeams = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);

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

  return { teams, loading };
};

export default useFetchTeams;
