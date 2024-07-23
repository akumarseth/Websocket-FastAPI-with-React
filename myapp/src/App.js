import './App.css';
import React, { useState, useEffect, useCallback } from 'react';
import { AreaChart, CartesianGrid, Area, XAxis, YAxis } from 'recharts';
import axios from 'axios';

const App = () => {
  const [data, setData] = useState([]);
  const [count, setCount] = useState(0);
  const [ws, setWs] = useState(null);
  const [intervalId, setIntervalId] = useState(null);

  const onMessage = useCallback((ev) => {
    const recv = JSON.parse(ev.data);
    console.log(recv);

    setData(prevData => {
      const newData = Array.isArray(prevData) ? [...prevData] : [];
      
      // Limit the number of data points to 20
      if (newData.length >= 20) {
        newData.shift(); // Remove the oldest entry if there are 20 entries
      }

      // Increment count based on the previous count value
      const newIndex = count;
      setCount(prevCount => prevCount + 1);

      // Add the new data point
      newData.push({ value: recv.value, index: newIndex });
      console.log(newData);
      return newData;
    });
  }, [count]);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/start-subscription');
      setData(response.data);

      const ws = new WebSocket('ws://localhost:8000/ws');
      ws.onmessage = onMessage;
      setWs(ws);

      const id = setInterval(() => ws.send('echo'), 1000);
      setIntervalId(id);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [ws, intervalId]);

  return (
    <div className="App">
      <header className="App-header">
        <h2>WebSocket Example</h2>
        <div>
          <button onClick={fetchData}>Fetch API Data</button>
        </div>
        <AreaChart width={900} height={600} data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#33ff33" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#33ff33" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="index" />
          <YAxis />
          <CartesianGrid stroke="#666" strokeDasharray="5 5" />
          <Area type="monotone" dataKey="value" stroke="#33ff33" fill="url(#colorValue)" isAnimationActive={false} />
        </AreaChart>
      </header>
    </div>
  );
};

export default App;
