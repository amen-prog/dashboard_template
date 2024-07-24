// src/components/WindRose.tsx

import React from 'react';
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Legend } from 'recharts';
import { ProcessedWindData } from '../../api/windyApi';

interface WindRoseProps {
  windData: ProcessedWindData[];
}

interface ChartWindData {
  direction: string;
  avgSpeed: number;
  avgGust: number;
}

interface DirectionData {
  direction: string;
  speeds: number[];
  gusts: number[];
}

const WindRose: React.FC<WindRoseProps> = ({ windData }) => {
  const processedData = processDataForWindRose(windData);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={processedData}>
        <PolarGrid gridType="polygon" stroke="#ccc" strokeDasharray="3 3" />
        <PolarAngleAxis dataKey="direction" stroke="#333" />
        <Radar name="Avg Wind Speed" dataKey="avgSpeed" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
        <Radar name="Avg Wind Gust" dataKey="avgGust" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
};

const processDataForWindRose = (windData: ProcessedWindData[]): ChartWindData[] => {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const directionData: DirectionData[] = directions.map(dir => ({
    direction: dir,
    speeds: [],
    gusts: []
  }));

  windData.forEach(data => {
    const index = Math.floor(((data.direction + 11.25) % 360) / 45);
    directionData[index].speeds.push(data.speed);
    directionData[index].gusts.push(data.gust);
  });

  return directionData.map(data => ({
    direction: data.direction,
    avgSpeed: data.speeds.length ? Number((data.speeds.reduce((a, b) => a + b) / data.speeds.length).toFixed(2)) : 0,
    avgGust: data.gusts.length ? Number((data.gusts.reduce((a, b) => a + b) / data.gusts.length).toFixed(2)) : 0
  }));
};

export default WindRose;
