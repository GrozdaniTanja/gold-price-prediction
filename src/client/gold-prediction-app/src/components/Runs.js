import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './../styles/Runs.css';

function Runs() {
    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

    useEffect(() => {
        const fetchRuns = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`${backendURL}/runs`);
                let responseData = response.data;

                console.log('Response data:', responseData); // Log the response
                console.log('Response data type:', typeof responseData);

                // Manually parse JSON if the response is a string
                if (typeof responseData === 'string') {
                    responseData = JSON.parse(responseData);
                }

                console.log('Parsed response data:', responseData);
                console.log('Is Array:', Array.isArray(responseData));

                if (Array.isArray(responseData)) {
                    setRuns(responseData);
                    setError(null); // Clear any previous error
                } else {
                    console.error('Expected an array but got:', responseData);
                    setError('Unexpected response format');
                    setRuns([]);
                }
            } catch (error) {
                console.error('Error fetching runs:', error);
                setError('Failed to fetch runs. Please try again later.');
                setRuns([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRuns();
    }, [backendURL]);

    const formatDate = (dateString) => {
        return new Date(dateString).toUTCString();
    };

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-3xl font-semibold mb-6">Runs</h2>
            {loading && <div className="text-lg text-gray-700 mb-6">Loading runs...</div>}
            {error && <div className="text-lg text-red-700 mb-6">{error}</div>}
            {!loading && !error && runs.length > 0 ? (
                runs.map((run) => (
                    <div key={run.run_id} className="mb-8">
                        <div
                            className={`p-6 rounded-lg shadow-lg transition-shadow duration-300 ${run.status === 'FINISHED'
                                ? 'bg-green-100 border border-green-500'
                                : 'bg-red-100 border border-red-500'
                                }`}
                        >
                            <p className="text-gray-700 mb-1">
                                <strong>Experiment Name:</strong> {run['params.experiment_name']}
                            </p>
                            <p className="text-gray-700 mb-1"><strong>Status:</strong> {run.status}</p>
                            <p className="text-gray-700 mb-1"><strong>Start Time:</strong> {formatDate(run.start_time)}</p>
                            <p className="text-gray-700 mb-1"><strong>MAE:</strong> {run['metrics.mae']}</p>
                            <p className="text-gray-700 mb-1"><strong>MSE:</strong> {run['metrics.mse']}</p>
                            <p className="text-gray-700 mb-1"><strong>R2:</strong> {run['metrics.r2']}</p>
                            <p className="text-gray-700 mb-1"><strong>N Estimators:</strong> {run['params.n_estimators']}</p>
                            <p className="text-gray-700 mb-1"><strong>Random State:</strong> {run['params.random_state']}</p>
                        </div>
                    </div>
                ))
            ) : (
                <div className="text-lg text-gray-700 mb-6">No runs available</div>
            )}
        </div>
    );
}

export default Runs;
