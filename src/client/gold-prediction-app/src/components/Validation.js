import React from 'react';

const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

const ValidationResults = () => {
    const validationReportURL = `${backendURL}/validation`;

    return (
        <div>
            <h2>Validation Results</h2>
            <button>
                <a href={validationReportURL} download>
                    Download Validation Report
                </a>
            </button>
        </div>
    );
};

export default ValidationResults;
