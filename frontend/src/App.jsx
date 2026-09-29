import { useState } from 'react';
import Dashboard from './Dashboard'

export default function App() {
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeMarket = async () => {
    setLoading(true);
    const response = await fetch('http://127.0.0.1:8000/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const result = await response.json();
    setData(result);
    setLoading(false);
  };

  return (
    <>
      <Dashboard />
      <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2>Quantitative Market Analyst</h2>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
        placeholder="Ask about a stock..." 
        style={{ width: '300px', padding: '0.5rem' }}
      />
      <button onClick={analyzeMarket} style={{ marginLeft: '1rem', padding: '0.5rem' }}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>

      {data && (
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
          <h1>{data.ticker} - {data.stance}</h1>
          <p>Current Price: ${data.current_price}</p>
          <h3>Key Observations:</h3>
          <ul>
            {data.key_observations.map((obs, i) => <li key={i}>{obs}</li>)}
          </ul>
        </div>
      )}
    </div>
    </>
    
  );
}

