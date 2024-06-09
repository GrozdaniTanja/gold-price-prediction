import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './../styles/Models.css';

function Models() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(false);
    const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

    useEffect(() => {
        const fetchModels = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`${backendURL}/models`);
                setModels(response.data);
            } catch (error) {
                console.error('Error fetching models:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchModels();
    }, [backendURL]);

    const groupedModels = models.reduce((acc, model) => {
        if (!acc[model.name]) {
            acc[model.name] = [];
        }
        acc[model.name].push(model);
        return acc;
    }, {});

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-3xl font-semibold mb-6">Models</h2>
            {loading && <div className="text-lg text-gray-700 mb-6">Loading models...</div>}
            {!loading && (
                Object.keys(groupedModels).map(name => (
                    <div key={name} className="mb-8">
                        <h3 className="text-2xl font-semibold mb-4">{name}</h3>
                        <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {groupedModels[name].map(model => (
                                <li key={model.version} className={`p-6 rounded-lg shadow-lg transition-shadow duration-300 ${model.current_stage === 'Production' ? 'bg-yellow-100 border border-yellow-500' : 'bg-white'}`}>
                                    <p className="text-gray-700 mb-1"><strong>Version:</strong> {model.version}</p>
                                    <p className="text-gray-700"><strong>Stage:</strong> {model.current_stage}</p>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))
            )}
        </div>
    );
}

export default Models;
