import { useState } from 'react';
import './App.css';

const API_URL = '/api/simulate';

function App() {
  const [formData, setFormData] = useState({
    cache_blocks: 8,
    block_size: 4,
    read_policy: 0,
    replacement_algorithm: 0,
    cache_access_time: 2,
    main_memory_access_time: 10,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: 'Unable to connect to backend server.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulator">
      <h1>Cache Simulator</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Cache Blocks:
          <input type="number" name="cache_blocks" value={formData.cache_blocks} onChange={handleChange} />
        </label>
        <label>
          Block Size:
          <input type="number" name="block_size" value={formData.block_size} onChange={handleChange} />
        </label>
        <label>
          Read Policy (0 = NLT, 1 = LT):
          <input type="number" name="read_policy" value={formData.read_policy} onChange={handleChange} />
        </label>
        <label>
          Replacement Algorithm (0 = LRU, 1 = MRU):
          <input type="number" name="replacement_algorithm" value={formData.replacement_algorithm} onChange={handleChange} />
        </label>
        <label>
          Cache Access Time:
          <input type="number" name="cache_access_time" value={formData.cache_access_time} onChange={handleChange} />
        </label>
        <label>
          Main Memory Access Time:
          <input type="number" name="main_memory_access_time" value={formData.main_memory_access_time} onChange={handleChange} />
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Run Simulation'}</button>
      </form>

      {result && (
        <div className="result">
          {result.error ? (
            <p className="error">{result.error}</p>
          ) : (
            <pre>{JSON.stringify(result, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
