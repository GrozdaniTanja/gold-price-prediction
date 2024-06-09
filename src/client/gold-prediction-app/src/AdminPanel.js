import React, { useState } from 'react';
import Models from './components/Models';
import ChangeStage from './components/ChangeStage';
import Experiments from './components/Experiments';
import Runs from './components/Runs';
import Testing from './components/Testing';
import Validation from './components/Validation';
import './AdminPanel.css';

function AdminPanel() {
    const [currentView, setCurrentView] = useState('Models');
    const menuItems = [
        { name: 'Home', view: 'Home', url: '/' },
        { name: 'Models', view: 'Models' },
        { name: 'Change Stage', view: 'ChangeStage' },
        { name: 'Experiments', view: 'Experiments' },
        { name: 'Runs', view: 'Runs' },
        { name: 'Testing', view: 'Testing' },
        { name: 'Validation', view: 'Validation' }
    ];

    const renderComponent = () => {
        switch (currentView) {
            case 'Models':
                return <Models />;
            case 'ChangeStage':
                return <ChangeStage />;
            case 'Experiments':
                return <Experiments />;
            case 'Runs':
                return <Runs />;
            case 'Testing':
                return <Testing />;
            case 'Validation':
                return <Validation />;
            default:
                return <Models />;
        }
    };

    return (
        <div className="admin-container">
            <header>
                <h1>Admin Panel</h1>
            </header>
            <nav>
                <ul className="menu">
                    {menuItems.map((item, index) => (
                        <li key={index}>
                            {item.url ? (
                                <a href={item.url}>{item.name}</a>
                            ) : (
                                <button onClick={() => setCurrentView(item.view)}>{item.name}</button>
                            )}
                        </li>
                    ))}
                </ul>
            </nav>
            <div className="content">
                {renderComponent()}
            </div>
        </div>
    );
}

export default AdminPanel;
