# Cache Simulator

## Structure

```
├── src/App.jsx          the whole website (form + results)
├── api/index.py         the server — receives form data, runs the simulation, sends back results
├── api/cache_simulator.py   the actual cache logic 
└── index.html            the page that loads App.jsx
```

The website (`src/`) and the server (`api/`) are two separate programs that talk to each other over the internet — the website sends the form numbers to `/api/simulate`, the server runs the simulation and sends the results back.

## Run locally

Open two terminals.

**Terminal 1 — backend**
```bash
cd api
pip install flask flask-cors
python index.py
```

**Terminal 2 — frontend**
```bash
npm install
npm run dev
```

Then open the URL it prints (usually `http://localhost:5173`).

Both terminals need to stay open while you're using it.

# Test Cases

## Sequential Sequence
## Mid-Repeat Blocks
## Random Sequence

