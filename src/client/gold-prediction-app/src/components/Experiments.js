import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './../styles/Experiments.css';

function Experiments() {
    const [experiments, setExperiments] = useState([]);
    const [loading, setLoading] = useState(false);
    const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

    useEffect(() => {
        const fetchExperiments = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`${backendURL}/experiments`);
                setExperiments(response.data);
            } catch (error) {
                console.error('Error fetching experiments:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchExperiments();
    }, [backendURL]);

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-3xl font-semibold mb-6">Experiments</h2>
            {loading && <div className="text-lg text-gray-700 mb-6">Loading experiments...</div>}
            <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {experiments.map((experiment) => (
                    <li
                        key={experiment.experiment_id}
                        className={`p-6 rounded-lg shadow-lg transition-shadow duration-300 ${experiment.lifecycle_stage === 'Production'
                            ? 'bg-yellow-100 border border-yellow-500'
                            : 'bg-white'
                            }`}
                    >
                        <h3 className="text-xl font-semibold mb-2">{experiment.name}</h3>
                        <p className="text-gray-700 mb-1">
                            <strong>ID:</strong> {experiment.experiment_id}
                        </p>
                        <p className="text-gray-700">
                            <strong>Stage:</strong> {experiment.lifecycle_stage}
                        </p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Experiments;
