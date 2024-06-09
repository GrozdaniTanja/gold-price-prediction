import React, { useState } from 'react';
import axios from 'axios';
import '../styles/ChangeStage.css';

function ChangeStage() {
    const [form, setForm] = useState({
        model_name: '',
        version: '',
        new_stage: ''
    });
    const [message, setMessage] = useState(null);
    const [loading, setLoading] = useState(false);

    const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({
            ...form,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post(`${backendURL}/change_model_stage`, form);
            setMessage(response.data.message);
        } catch (error) {
            console.error('Error changing model stage:', error);
            setMessage('Error changing model stage');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-3xl font-semibold mb-6">Change Model Stage</h2>
            <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg">
                <div className="form-group mb-4">
                    <label htmlFor="model_name" className="block mb-2 text-lg font-medium text-gray-700">Model Name:</label>
                    <input type="text" name="model_name" value={form.model_name} onChange={handleChange} className="form-input w-full" required />
                </div>
                <div className="form-group mb-4">
                    <label htmlFor="version" className="block mb-2 text-lg font-medium text-gray-700">Version:</label>
                    <input type="text" name="version" value={form.version} onChange={handleChange} className="form-input w-full" required />
                </div>
                <div className="form-group mb-6">
                    <label htmlFor="new_stage" className="block mb-2 text-lg font-medium text-gray-700">New Stage:</label>
                    <select name="new_stage" value={form.new_stage} onChange={handleChange} className="form-select w-full" required>
                        <option value="">Select a stage</option>
                        <option value="None">None</option>
                        <option value="Staging">Staging</option>
                        <option value="Production">Production</option>
                        <option value="Archived">Archived</option>
                    </select>
                </div>
                <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" disabled={loading}>
                    {!loading ? 'Change Stage' : 'Loading...'}
                </button>
            </form>
            {message && <div className="mt-4 text-lg text-green-700">{message}</div>}
        </div>
    );
}

export default ChangeStage;
