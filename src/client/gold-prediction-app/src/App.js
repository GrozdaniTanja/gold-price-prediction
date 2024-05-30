import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import './App.css';

function App() {
  const [days, setDays] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/predict', { days });
      setPredictions(response.data.predictions);
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
      </header>
    </div>
  );
}

export default App;
