 
import { useEffect, useState } from 'react';
import { fetchReports } from '../api/reporting';

const useFetchReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getReports = async () => {
      try {
        const reportsData = await fetchReports();
        setReports(reportsData);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error fetching reports:', error);
      }
    };
    getReports();
  }, []);

  return { reports, loading };
};

export default useFetchReports;
