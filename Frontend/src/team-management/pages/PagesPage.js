
import React, { useEffect, useState } from 'react';
import { fetchPages } from '../api/pageBuilder';

const PagesPage = () => {
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPages = async () => {
      try {
        const pagesData = await fetchPages();
        setPages(pagesData);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error fetching pages:', error);
      }
    };
    getPages();
  }, []);

  if (loading) return <div>Loading pages...</div>;

  return (
    <div>
      <h2>Your Pages</h2>
      <ul>
        {pages.map(page => (
          <li key={page.id}>
            <h3>{page.name}</h3>
            <button>Edit</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PagesPage;
