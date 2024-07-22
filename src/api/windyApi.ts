// src/api/windyApi.ts

const API_KEY = 'rB2jpuNEYEy3esdNyrGxVlYatpAuSeqV';
const API_URL = 'https://api.windy.com/api/point-forecast/v2';

export interface ProcessedWindData {
  speed: number;
  direction: number;
  gust: number;
  timestamp: number;
}

export const getWindData = (
  latitude: number, 
  longitude: number, 
  callback: (data: ProcessedWindData[] | null, error: Error | null) => void
) => {
  const requestBody = {
    lat: latitude,
    lon: longitude,
    model: "gfs",
    parameters: ["wind", "windGust"],
    levels: ["surface"],
    key: API_KEY
  };

  fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })
  .then(response => response.json())
  .then(data => {
    console.log('API Response:', data);
    const processedData = processWindData(data);
    callback(processedData, null);
  })
  .catch(error => {
    console.error('Error fetching wind data:', error);
    callback(null, error);
  });
};

const processWindData = (data: any): ProcessedWindData[] => {
  const windU = data['wind_u-surface'];
  const windV = data['wind_v-surface'];
  console.log('wind_v:', windV);
  const windGust = data['gust-surface'];
  const timestamps = data.ts;

  if (windU && windV && windGust && timestamps) {
    return windU.map((u: number, index: number) => {
      const v = windV[index];
      const speed = Math.sqrt(u*u + v*v);
      const direction = (270 - (Math.atan2(v, u) * 180 / Math.PI)) % 360;
      return {
        speed: Number(speed.toFixed(2)),
        direction: Number(direction.toFixed(2)),
        gust: Number(windGust[index].toFixed(2)),
        timestamp: timestamps[index]
      };
    });
  } else {
    console.log('Unexpected data structure:', data);
    return [];
  }
};