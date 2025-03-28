import axios from 'axios';

export const checkGeoLocation = async (ip: string): Promise<boolean> => {
  const response = await axios.get(\`http://ip-api.com/json/\${ip}\`);
  const country = response.data.countryCode;
  return country === 'BR'; // Apenas Brasil autorizado
};
