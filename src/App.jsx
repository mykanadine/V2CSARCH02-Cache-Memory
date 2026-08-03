import { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = '/api/simulate';

// mirrors the backend's is_positive_power_of_two_min4 / is_positive_power_of_two
// checks, so the stepper inputs below can never land on a value the backend
// would reject
const MIN_CACHE_BLOCKS = 4;
const MIN_BLOCK_SIZE = 2;

function App() {
  // form fields for the simulation config, sent straight to the backend on submit
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
  // 'snapshot' = just show the final cache state, 'animate' = step through the trace.
  // this is one shared toggle above all 3 test cases, not per-card
  const [viewMode, setViewMode] = useState('snapshot');

  // generic input handler, works for any field since we key off e.target.name
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // same shape as handleChange, but for inputs that already know their own
  // name/value (e.g. PowerOfTwoInput's stepper buttons) instead of reading
  // off a DOM event
  const setField = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // sends the form config to the flask backend and stores whatever comes back
  // (either the 3-test-case results, or an error message)
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
        <PowerOfTwoInput
          label="Cache Blocks:"
          name="cache_blocks"
          value={formData.cache_blocks}
          min={MIN_CACHE_BLOCKS}
          onChange={setField}
        />
        <PowerOfTwoInput
          label="Block Size:"
          name="block_size"
          value={formData.block_size}
          min={MIN_BLOCK_SIZE}
          onChange={setField}
        />
        <label>
          Read Policy:
          <select name="read_policy" value={formData.read_policy} onChange={handleChange}>
            <option value={0}>0 = NLT (Not Load-Through)</option>
            <option value={1}>1 = LT (Load-Through)</option>
          </select>
        </label>
        <label>
          Replacement Algorithm:
          <select name="replacement_algorithm" value={formData.replacement_algorithm} onChange={handleChange}>
            <option value={0}>0 = LRU (Least Recently Used)</option>
            <option value={1}>1 = MRU (Most Recently Used)</option>
          </select>
        </label>
        <label>
          Cache Access Time:
          <input type="number" name="cache_access_time" min="1" step="1" value={formData.cache_access_time} onChange={handleChange} />
        </label>
        <label>
          Main Memory Access Time:
          <input type="number" name="main_memory_access_time" min="1" step="1" value={formData.main_memory_access_time} onChange={handleChange} />
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Run Simulation'}</button>
      </form>

      {result && !result.error && (
        // toggle sits above the results so it applies to all 3 test cases at once
        <div className="view-toggle">
          <span>View:</span>
          <button
            type="button"
            className={viewMode === 'snapshot' ? 'toggle-btn active' : 'toggle-btn'}
            onClick={() => setViewMode('snapshot')}
          >
            Final Snapshot
          </button>
          <button
            type="button"
            className={viewMode === 'animate' ? 'toggle-btn active' : 'toggle-btn'}
            onClick={() => setViewMode('animate')}
          >
            Step-by-Step Animation
          </button>
        </div>
      )}

      {result && (
        <div className="result">
          {result.error ? (
            <p className="error">{result.error}</p>
          ) : (
            <div className="test-cases">
              <TestCaseResult title="Sequential" data={result.test_cases.sequential} viewMode={viewMode} />
              <TestCaseResult title="Mid-Repeat" data={result.test_cases.mid_repeat} viewMode={viewMode} />
              <TestCaseResult title="Random" data={result.test_cases.random} viewMode={viewMode} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// number input restricted to powers of two (>= min), matching what the
// backend actually accepts for cache_blocks/block_size. no custom UI here —
// clicking the native spinner arrows (or pressing the up/down keys) always
// changes a number input's value by exactly the default step of 1, so that's
// caught in onChange and turned into a doubled/halved value instead. typing
// is left alone until blur, where it gets snapped to the nearest valid
// power of two so an invalid value can never be submitted
function PowerOfTwoInput({ label, name, value, min, onChange }) {
  const nearestPowerOfTwo = (raw) => {
    const n = Number(raw);
    if (!Number.isFinite(n) || n < min) return min;
    return Math.max(min, 2 ** Math.round(Math.log2(n)));
  };

  const handleChange = (e) => {
    const raw = e.target.value;
    const oldValue = Number(value) || min;
    const diff = Number(raw) - oldValue;

    if (diff === 1) {
      onChange(name, Math.max(min, oldValue * 2));
    } else if (diff === -1) {
      onChange(name, Math.max(min, oldValue / 2));
    } else {
      onChange(name, raw);
    }
  };

  return (
    <label>
      {label}
      <input
        type="number"
        name={name}
        value={value}
        onChange={handleChange}
        onBlur={(e) => onChange(name, nearestPowerOfTwo(e.target.value))}
      />
    </label>
  );
}

// one card per test case (sequential / mid-repeat / random). shows the stats
// plus either the snapshot or animation view, depending on the shared toggle
function TestCaseResult({ title, data, viewMode }) {
  return (
    <div className="test-case-card">
      <h2>{title}</h2>
      <div className="stats-grid">
        <div><span>Total Accesses: </span><strong>{data.total_accesses}</strong></div>
        <div><span>Hits: </span><strong>{data.hit_count}</strong></div>
        <div><span>Misses: </span><strong>{data.miss_count}</strong></div>
        <div><span>Hit Rate: </span><strong>{(data.hit_rate * 100).toFixed(2)}%</strong></div>
        <div><span>Miss Rate: </span><strong>{(data.miss_rate * 100).toFixed(2)}%</strong></div>
        <div><span>Avg. Memory Access Time: </span><strong>{data.average_memory_access_time.toFixed(3)}</strong></div>
        <div><span>Total Memory Access Time: </span><strong>{data.total_memory_access_time.toFixed(3)}</strong></div>
        <div><span>Execution Time (s)</span><strong>{data.execution_time_seconds.toFixed(6)}</strong></div>
      </div>

      {viewMode === 'snapshot' ? (
        <FinalSnapshot cacheState={data.final_cache_state} accessSequence={data.access_sequence} />
      ) : (
        <StepAnimation
          traceLog={data.trace_log}
          cacheBlocks={data.final_cache_state.length}
          accessSequence={data.access_sequence}
        />
      )}

      <details>
        <summary>Full trace log ({data.trace_log.length} steps)</summary>
        <TraceLogList traceLog={data.trace_log} />
      </details>
    </div>
  );
}

// styled list version of the trace log, one row per access
function TraceLogList({ traceLog }) {
  return (
    <div className="trace-log-list">
      {traceLog.map((entry) => (
        <div key={entry.step} className="trace-row">
          <span className="trace-step">#{entry.step + 1}</span>
          <span className="trace-block">Block {entry.block}</span>
          <span className={entry.result === 'HIT' ? 'result-tag hit' : 'result-tag miss'}>
            {entry.result}
          </span>
          <span className="trace-cache">[{entry.cache_state.map((b) => (b === null ? '—' : b)).join(', ')}]</span>
        </div>
      ))}
    </div>
  );
}

// just shows the cache slots as they ended up, no animation.
// lists the full access sequence plainly (no highlighting, since
// there's no "current step" in a snapshot view)
function FinalSnapshot({ cacheState, accessSequence }) {
  return (
    <div>
      <p className="final-cache-label">
        Main Memory Sequence: <span className="sequence-list">{accessSequence.join(', ')}</span>
      </p>
      <p className="final-cache-label">Final Cache State:</p>
      <div className="cache-row">
        {cacheState.map((block, idx) => (
          <div key={idx} className={block === null ? 'cache-slot empty' : 'cache-slot filled'}>
            <span className="slot-index">{idx}</span>
            <span className="slot-value">{block === null ? '—' : block}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// how many ms one "step" takes at 1x speed. actual delay = BASE_DELAY_MS / speedMultiplier
const BASE_DELAY_MS = 600;

// steps through the trace log one access at a time, with play/pause controls
function StepAnimation({ traceLog, cacheBlocks, accessSequence }) {
  // stepIndex = -1 means "before the first access" (empty cache, nothing highlighted yet)
  const [stepIndex, setStepIndex] = useState(-1);
  const [playing, setPlaying] = useState(false);
  // 1x = normal speed (BASE_DELAY_MS per step). 0.25x = slowest (4x slower),
  // 5x = fastest (5x faster than normal). default starts at a normal 1x pace
  const [speedMultiplier, setSpeedMultiplier] = useState(1);
  // holds the setInterval id so we can clear it later. useRef instead of state
  // because changing it shouldn't trigger a re-render on its own
  const intervalRef = useRef(null);
  // points at whichever cache-slot div is currently highlighted, so the
  // effect below can scroll it into view as the animation steps through
  // (cache-row is capped height + overflow-y: auto for large caches)
  const highlightRef = useRef(null);

  const lastIndex = traceLog.length - 1;
  const atEnd = stepIndex >= lastIndex;
  const delayMs = BASE_DELAY_MS / speedMultiplier;

  // effect that drives the animation: while "playing" is true,
  // it sets up a timer that bumps stepIndex forward every delayMs milliseconds.
  // re-runs whenever playing, lastIndex, or the speed changes (so dragging the
  // slider while playing correctly restarts the timer at the new speed)
  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setStepIndex((prev) => {
          // hit the last step? stop auto-playing instead of going out of bounds
          if (prev >= lastIndex) {
            setPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, delayMs);
    }
    // clear the old interval whenever playing/speed changes or the
    // component unmounts, so never end up with multiple timers running
    return () => clearInterval(intervalRef.current);
  }, [playing, lastIndex, delayMs]);

  // keeps the highlighted slot scrolled into view inside cache-row as
  // stepIndex changes, so it stays visible even when the cache is tall
  // enough to scroll (play, step forward, and step back all update stepIndex)
  useEffect(() => {
    if (highlightRef.current) {
      highlightRef.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [stepIndex]);

  const handlePlayPause = () => {
    if (atEnd) {
      // if already at the end and they hit play again, just start over
      setStepIndex(-1);
      setPlaying(true);
    } else {
      setPlaying((p) => !p);
    }
  };

  const handleStepForward = () => {
    setPlaying(false); // manual stepping should pause any auto-play in progress
    setStepIndex((prev) => Math.min(prev + 1, lastIndex));
  };

  const handleStepBack = () => {
    setPlaying(false);
    setStepIndex((prev) => Math.max(prev - 1, -1));
  };

  const handleReset = () => {
    setPlaying(false);
    setStepIndex(-1);
  };

  // before the first step, cache is just empty slots (nothing accessed yet)
  const emptyCache = Array(cacheBlocks).fill(null);
  const currentEntry = stepIndex >= 0 ? traceLog[stepIndex] : null;
  const cacheState = currentEntry ? currentEntry.cache_state : emptyCache;

  // figure out which slot to highlight: wherever the accessed block landed this step
  // (for a HIT it's just where the block already was, for a MISS it's the slot it got placed/replaced into)
  const highlightIdx = currentEntry ? cacheState.indexOf(currentEntry.block) : -1;

  // running hit/miss count up through the current step, so the counter updates
  // live as the animation plays instead of just showing the final totals
  const stepsSoFar = traceLog.slice(0, stepIndex + 1);
  const hitsSoFar = stepsSoFar.filter((entry) => entry.result === 'HIT').length;
  const missesSoFar = stepsSoFar.length - hitsSoFar;

  return (
    <div className="step-animation-layout">
      {/* left column: step text + the (scrollable) main memory sequence, so a
          long sequence doesn't push the whole page down */}
      <div className="step-info-panel">
        <p className="step-label">Step: {currentEntry ? stepIndex + 1 : '—'}</p>

        <p className="step-label">Main Memory Sequence:</p>
        {/* full access sequence, with the block for the current step highlighted in place.
            capped height + scroll so long sequences (e.g. the 128-step random test case)
            stay contained instead of stretching the page */}
        <div className="sequence-box">
          <span className="sequence-list">
            {accessSequence.map((block, idx) => (
              <span key={idx}>
                <span className={idx === stepIndex ? 'sequence-item current' : 'sequence-item'}>
                  {block}
                </span>
                {idx < accessSequence.length - 1 ? ', ' : ''}
              </span>
            ))}
          </span>
        </div>

        <p className="step-label">
          {currentEntry ? (
            <>
              Block {currentEntry.block} →{' '}
              <span className={currentEntry.result === 'HIT' ? 'result-tag hit' : 'result-tag miss'}>
                {currentEntry.result}
              </span>
            </>
          ) : (
            `Ready (${traceLog.length} steps total)`
          )}
        </p>

        {/* live hit/miss tally, sits right under the step result since the
            sequence box above is already scrollable and has room to spare */}
        <div className="live-counter">
          <div className="live-counter-item hit">
            <span className="live-counter-label">Hits</span>
            <span className="live-counter-value">{hitsSoFar}</span>
          </div>
          <div className="live-counter-item miss">
            <span className="live-counter-label">Misses</span>
            <span className="live-counter-value">{missesSoFar}</span>
          </div>
        </div>
      </div>

      {/* right column: cache slots (scrollable if there are a lot of them),
          then playback controls and speed slider underneath */}
      <div className="animation-panel">
        {/* cache visualization: one box per cache block, highlighting whichever one
            just changed. stacked vertically, capped height + scroll so a large cache
            (e.g. 16+ blocks) doesn't push the controls off screen */}
        <div className="cache-row">
          {cacheState.map((block, idx) => (
            <div
              key={idx}
              ref={idx === highlightIdx ? highlightRef : null}
              className={
                'cache-slot ' +
                (block === null ? 'empty' : 'filled') +
                (idx === highlightIdx ? (currentEntry.result === 'HIT' ? ' pulse-hit' : ' pulse-miss') : '')
              }
            >
              <span className="slot-index">{idx}</span>
              <span className="slot-value">{block === null ? '—' : block}</span>
            </div>
          ))}
        </div>

        {/* playback buttons: reset, step back, play/pause, step forward */}
        <div className="animation-controls">
          <button type="button" onClick={handleReset} title="Reset to start">⏮</button>
          <button type="button" onClick={handleStepBack} disabled={stepIndex < 0} title="Step back">◀</button>
          <button type="button" onClick={handlePlayPause} title="Play / Pause">
            {playing ? '⏸ Pause' : atEnd ? '↻ Replay' : '▶ Play'}
          </button>
          <button type="button" onClick={handleStepForward} disabled={atEnd} title="Step forward">▶</button>
          <span className="step-counter">{stepIndex + 1} / {traceLog.length}</span>
        </div>

        {/* speed slider: 0.25x (slowest) up to 5x (fastest), defaults to a normal 1x pace */}
        <div className="speed-control">
          <label htmlFor={`speed-${cacheBlocks}-${traceLog.length}`}>Speed</label>
          <input
            id={`speed-${cacheBlocks}-${traceLog.length}`}
            type="range"
            min="0.25"
            max="5"
            step="0.25"
            value={speedMultiplier}
            onChange={(e) => setSpeedMultiplier(Number(e.target.value))}
          />
          <span className="speed-label">{speedMultiplier.toFixed(2)}x</span>
        </div>
      </div>
    </div>
  );
}

export default App;