 
import React, { useEffect, useState } from 'react';
import { fetchReports } from '../api/reporting';

const ReportsPage = () => {
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

  if (loading) return <div>Loading reports...</div>;

  return (
    <div>
      <h2>Reports</h2>
      <ul>
        {reports.map(report => (
          <li key={report.id}>
            <h3>{report.title}</h3>
            <p>{report.date}</p>
            <button>View</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ReportsPage;
