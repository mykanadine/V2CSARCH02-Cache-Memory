# Cache Simulator

## Structure

```
├── src/App.jsx          the whole website (form + results)
├── src/main.jsx         loads App.jsx into the page
├── api/index.py         the server — cache simulation logic + Flask API that runs it, all in one file
├── index.html            the page that loads App.jsx
└── vercel.json           tells Vercel to route /api/* requests to api/index.py
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

## Parameters
| Parameter | Type | Specification |
|---|---|---|
| Cache Mapping Function | Fixed | Fully Associative |
| Main Memory Size | Fixed | 1024 blocks |
| Cache Blocks | Parameterized | Minimum 4 blocks; power of 2 |
| Block Size | Parameterized | Minimum 2 words; power of 2 |
| Read Policy | Parameterized | Load-through or Non-load-through |
| Replacement Algorithm | Parameterized | Least Recently Used (LRU) or Most Recently Used (MRU) |
| Cache Access Time | Parameterized | Greater than 0 |
| Main Memory Access Time | Parameterized | Greater than 0 |
# Test Cases
![NLT LRU Snapshot](`screenshots/NLT-LRU-Snapshot.png`)
## Sequential Sequence
## Mid-Repeat Blocks
## Random Sequence

