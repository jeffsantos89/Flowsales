 
import React, { useEffect, useState } from 'react';
import { fetchPixels, addPixel } from '../api/pixel';

const PixelsPage = () => {
  const [pixels, setPixels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [platform, setPlatform] = useState('');
  const [event, setEvent] = useState('');

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

  const handleAddPixel = async () => {
    try {
      const newPixel = await addPixel(platform, event);
      setPixels([...pixels, newPixel]);
    } catch (error) {
      console.error('Error adding pixel:', error);
    }
  };

  if (loading) return <div>Loading pixels...</div>;

  return (
    <div>
      <h2>Pixels Configuration</h2>
      <ul>
        {pixels.map(pixel => (
          <li key={pixel.id}>
            <p>{pixel.platform} - {pixel.event}</p>
          </li>
        ))}
      </ul>
      <h3>Add New Pixel</h3>
      <input 
        type="text" 
        placeholder="Platform (e.g. Facebook)" 
        value={platform} 
        onChange={(e) => setPlatform(e.target.value)} 
      />
      <input 
        type="text" 
        placeholder="Event (e.g. Page View)" 
        value={event} 
        onChange={(e) => setEvent(e.target.value)} 
      />
      <button onClick={handleAddPixel}>Add Pixel</button>
    </div>
  );
};

export default PixelsPage;
