
import { useEffect, useState } from 'react';
import { fetchPages } from '../api/pageBuilder';

const useFetchPages = () => {
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

  return { pages, loading };
};

export default useFetchPages;
