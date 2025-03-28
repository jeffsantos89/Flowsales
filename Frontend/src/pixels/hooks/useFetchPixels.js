 
import { useEffect, useState } from 'react';
import { fetchPixels } from '../api/pixel';

const useFetchPixels = () => {
  const [pixels, setPixels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPixels = async () => {
      try {
        const pixelsData = await fetchPixels();
        setPixels(pixelsData);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error fetching pixels:', error);
      }
    };
    getPixels();
  }, []);

  return { pixels, loading };
};

export default useFetchPixels;
