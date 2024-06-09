import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './../styles/Testing.css';

function Testing() {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

    useEffect(() => {
        const fetchResults = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`${backendURL}/testing`);
                setResults(response.data);
            } catch (error) {
                console.error('Error fetching testing results:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [backendURL]);

    const getResultCardColor = (result) => {
        if (!result.summary || !result.summary.all_passed) return 'bg-white';
        return result.summary.all_passed ? 'bg-green-100 border border-green-500' : 'bg-red-100 border border-red-500';
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toUTCString();
    };

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-3xl font-semibold mb-6">Testing Results</h2>
            {loading && <div className="text-lg text-gray-700 mb-6">Loading testing results...</div>}
            {!loading && results.map((result, index) => (
                <div key={index} className="mb-4">
                    <div className={`p-6 rounded-lg shadow-lg transition-shadow duration-300 ${getResultCardColor(result)}`}>
                        {result.summary && (
                            <>
                                <p className="text-lg font-semibold mb-2">Summary</p>
                                <p className="text-gray-700"><strong>All Passed:</strong> {result.summary.all_passed ? 'Yes' : 'No'}</p>
                                <p className="text-gray-700"><strong>Total Tests:</strong> {result.summary.total_tests}</p>
                                <p className="text-gray-700"><strong>Success Tests:</strong> {result.summary.success_tests}</p>
                                <p className="text-gray-700"><strong>Failed Tests:</strong> {result.summary.failed_tests}</p>
                            </>
                        )}
                        {result.tests && (
                            <>
                                <p className="text-gray-700"><strong>Date and time:</strong> {formatDate(result.timestamp)}</p>
                                <p className="text-lg font-semibold mt-4 mb-2">Tests</p>
                                {result.tests.map((test, idx) => (
                                    <div key={idx}>
                                        <p className="text-gray-700"><strong>Name:</strong> {test.name}</p>
                                        <p className="text-gray-700"><strong>Description:</strong> {test.description}</p>
                                        <p className="text-gray-700"><strong>Group:</strong> {test.group}</p>
                                        <p className="text-gray-700"><strong>Status:</strong> {test.status}</p>
                                        <p className="text-gray-700"><strong>Parameters:</strong> {JSON.stringify(test.parameters)}</p>
                                        <hr className="my-2 border-gray-200" />
                                    </div>
                                ))}
                            </>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default Testing;
