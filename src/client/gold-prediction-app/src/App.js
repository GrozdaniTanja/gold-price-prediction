import React, { useState } from 'react';
import {
  BrowserRouter as Router, Route, Routes, Switch, Link
} from 'react-router-dom';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import './App.css';
import AdminPanel from '../src/AdminPanel';

function Home() {
  const [days, setDays] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const daysInt = parseInt(days, 10); // Convert days to an integer
      const response = await axios.post('http://localhost:5000/predict', { days: daysInt });
      setPredictions(response.data.prediction);
      setError(null);
    } catch (err) {
      setError('Error fetching predictions');
    }
  };

  const data = {
    labels: predictions.map((_, index) => `Day ${index + 1}`),
    datasets: [
      {
        label: 'Gold Price Prediction',
        data: predictions,
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
    ],
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Gold Price Prediction</h1>
        <form onSubmit={handleSubmit}>
          <label>
            Enter number of days for forecasting:
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(e.target.value)}
              required
            />
          </label>
          <button type="submit">Predict</button>
        </form>
        {error && <p className="error">{error}</p>}
        {predictions.length > 0 && (
          <>
            <Line data={data} />
            <div className="predictions">
              <h2>Predictions:</h2>
              <ul>
                {predictions.map((prediction, index) => (
                  <li key={index}>Day {index + 1}: {prediction}</li>
                ))}
              </ul>
            </div>
          </>
        )}
        <nav>
          <Link to="/admin">Admin Panel</Link>
        </nav>
      </header>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Router>
  );
}

export default App;
