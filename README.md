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

## Parameters & Outputs
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

output table...

## Test Cases (Let n be the total number of cache blocks)
### Sequential Sequence
Access Order: 0 to 2n-1 repeated twice

**LRU vs MRU Behavior**

Example: n=4 (0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7)

First Half First Pass: 0,1,2,3

Second Half First Pass: 4,5,6,7

First Half Second Pass: 0,1,2,3

Second Half Second Pass: 4,5,6,7

**LRU**: The cache fills from top to bottom during the first half of the first pass until it becomes full (Cache: 0,1,2,3). As the second half of the first pass is accessed, those new blocks replace the whole first-half blocks from top to bottom (Cache: 4,5,6,7). When the second pass begins, the first-half blocks are no longer in the cache, so they all miss and replace the second-half blocks of the first pass (Cache: 0,1,2,3). Similarly, when the second half of the second pass is accessed, the second-half blocks of the first pass have already been evicted by the first-half blocks of the second pass (Cache: 4,5,6,7). As a result, every access is a cache miss, giving an overall 0% hit rate.

**MRU**: The cache fills from top to bottom during the first half of the first pass until it becomes full (Cache: 0,1,2,3). As the second half of the first pass is accessed, the most recently used block, which is the last position, will be continuously modified until the end of the second half first pass (Cache: 0,1,2,7). When the second pass first half begins, the blocks except for the last block in the first half will hit. Since it's most recently used, the second to the last position will be replaced by the last block in first half second pass (Cache: 0,1,3,7). When the second half of the second pass is accessed, the most recently used is still the second to the last position. This position will be continuously modified until the last block of the second half hit the last block (Cache: 0,1,6,7). This results in a higher hit rate than LRU.

### Mid-Repeat Blocks
### Random Sequence

## Simulation Screenshots

### Step-by-Step Animation Views (LT MRU, NLT MRU, LT LRU, NLT LRU)
![LT MRU Animation](screenshots/LT-MRU-Animation.png)
![NLT MRU Animation](screenshots/NLT-MRU-Animation.png)
![LT LRU Animation](screenshots/LT-LRU-Animation.png)
![NLT LRU Animation](screenshots/NLT-LRU-Animation.png)

### Final Snapshot Views (LT MRU, NLT MRU, LT LRU, NLT LRU)
![LT MRU Snapshot](screenshots/LT-MRU-Snapshot.png)
![NLT MRU Snapshot](screenshots/NLT-MRU-Snapshot.png)
![LT LRU Snapshot](screenshots/LT-LRU-Snapshot.png)
![NLT LRU Snapshot](screenshots/NLT-LRU-Snapshot.png)

### Different Timing Values (Cache Access Time & Memory Access Time)
![NLT MRU Different Timing Values 1](screenshots/NLT-MRU-Diff-Values-(Cache-Access-Time-&-Main-Memory-Access-Time)-Animation.png)
![NLT MRU Different Timing Values 2](screenshots/NLT-MRU-Diff-Values-(Cache-Access-Time-&-Main-Memory-Access-Time)-Snapshot.png)

### Edge Cases (Minimum Values)
![NLT LRU Edge Case Animation](screenshots/NLT-LRU-Edge-Case-(Min-values)-Animation.png)
![NLT LRU Edge Case Snapshot](screenshots/NL-LRU-Edge-Case-(Min-values)-Snapshot.png)

