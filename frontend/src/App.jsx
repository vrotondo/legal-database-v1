import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [backendData, setBackendData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Test connection to backend
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/test');
        setBackendData(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to connect to backend');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Legal Case Management System</h1>

        {loading && <p>Connecting to backend...</p>}

        {error && <p style={{ color: 'red' }}>{error}</p>}

        {backendData && (
          <div>
            <p style={{ color: 'green' }}>✅ Connected to backend!</p>
            <p>{backendData.message}</p>
            <div>
              <h3>Sample Data:</h3>
              <ul>
                {backendData.data.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;