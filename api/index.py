import time
import random

# perf_counter (not time.time) since it's a high-resolution monotonic clock,
# needed because these simulations often finish in well under a millisecond,
# which time.time() can't reliably measure on all platforms
from flask import Flask, jsonify, request
from flask_cors import CORS

MAIN_MEMORY = 1024


# makes a list of random block numbers (0-1023, since that's our main memory size)
# only used for the "random" test case
def generate_random_sequence(accesses):
    sequence = []
    for _ in range(accesses):
        sequence.append(random.randint(0, 1023))

    return sequence


class CacheSimulator:
    def __init__(self, cache_blocks, block_size, read_policy, replacement_algorithm, cache_access_time, main_memory_access_time):
        self.cache_blocks = cache_blocks
        self.block_size = block_size
        self.read_policy = read_policy  # NLT (0) OR LT (1)
        self.replacement_algorithm = replacement_algorithm  # LRU (0) OR MRU (1)
        self.cache_access_time = cache_access_time
        self.main_memory_access_time = main_memory_access_time
        self.view = False  # False = final snapshot, True = step-by-step

        self.reset()

    def reset(self):
        # wipes the cache clean so each test case starts from scratch
        # otherwise stats from one test case bleed into the next one
        self.cache = [None] * self.cache_blocks
        self.counter = [None] * self.cache_blocks
        self.miss_count = 0
        self.hit_count = 0
        self.trace_log = []
        self.access_counter = 0  # keeps counting up across multiple access_cache() calls, doesn't reset per call

    def cache_hit(self, ctr, block):
        # block's already in the cache, just update when it was last used
        idx = self.cache.index(block)
        self.counter[idx] = ctr
        self.hit_count += 1
        self.trace_log.append({"step": ctr, "block": block, "result": "HIT", "cache_state": list(self.cache)})

    def cache_miss(self, ctr, block):
        # if there's an empty slot, put block in cache block
        if None in self.cache:
            idx = self.cache.index(None)

        # cache is full, replace block
        else:
            idx = self.replace_block()

        self.cache[idx] = block
        self.counter[idx] = ctr
        self.miss_count += 1
        self.trace_log.append({"step": ctr, "block": block, "result": "MISS", "cache_state": list(self.cache)})

    def replace_block(self):
        # LRU -> kick out whoever has the smallest (oldest) counter value
        if self.replacement_algorithm == 0:
            return self.counter.index(min(self.counter))
        # MRU -> kick out whoever was JUST used (largest counter value)
        else:
            return self.counter.index(max(self.counter))

    def access_cache(self, access_sequence):
        # walk through the sequence one block at a time, checking hit or miss
        # (uses self.access_counter so the count keeps counting up even
        # across multiple access_cache() calls, e.g. pass 1 then pass 2)
        for block in access_sequence:
            ctr = self.access_counter
            if block in self.cache:
                self.cache_hit(ctr, block)
            else:
                self.cache_miss(ctr, block)
            self.access_counter += 1

    # bundles up all the current stats into one dict, so each test case
    # can grab its own snapshot right after it runs (before the next
    # test case resets everything)
    def stats_snapshot(self, execution_time_seconds):
        return {
            "final_cache_state": list(self.cache),
            "total_accesses": self.total_accesses,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "average_memory_access_time": self.average_memory_access_time,
            "total_memory_access_time": self.total_memory_access_time,
            "execution_time_seconds": execution_time_seconds,
            "trace_log": self.trace_log,
        }

    # --- TEST CASES ---
    # Each test case resets cache state first so results are isolated
    # and not cumulative across test cases.

    def simulate_sequential(self):
        self.reset()

        # just 0, 1, 2, ... up to 2n-1 in order. NOT random.
        # e.g. if n=4 -> 0,1,2,3,4,5,6,7
        access_sequence = []
        for i in range(self.cache_blocks * 2):
            access_sequence.append(i)

        start_time = time.perf_counter()
        # run it twice, per the spec (so blocks that fell out on round 1
        # can come back as hits/misses on round 2)
        self.access_cache(access_sequence)
        self.access_cache(access_sequence)
        elapsed = time.perf_counter() - start_time

        result = self.stats_snapshot(elapsed)
        # it ran twice, so the "full" sequence for display/highlighting purposes
        # needs to be doubled too, otherwise it won't line up with trace_log
        result["access_sequence"] = access_sequence + access_sequence
        return result

    def simulate_mid_repeat(self):
        self.reset()
        access_sequence_1 = []
        access_sequence_2 = []

        # sequence 1: 0 to n-1 (that's n values total, since we start at 0)
        for i in range(self.cache_blocks):
            access_sequence_1.append(i)

        # sequence 2: 0 to 2n-1 (2n values total)
        for i in range(self.cache_blocks * 2):
            access_sequence_2.append(i)

        full_sequence = []  # just for keeping track of what we actually ran, for the trace/log

        start_time = time.perf_counter()

        # run seq1 once, then seq2 twice
        self.access_cache(access_sequence_1)
        full_sequence += access_sequence_1

        self.access_cache(access_sequence_2)
        full_sequence += access_sequence_2
        self.access_cache(access_sequence_2)
        full_sequence += access_sequence_2

        # now flip both sequences around and do the same thing backwards
        access_sequence_1.reverse()
        self.access_cache(access_sequence_1)
        full_sequence += access_sequence_1

        access_sequence_2.reverse()
        self.access_cache(access_sequence_2)
        full_sequence += access_sequence_2
        self.access_cache(access_sequence_2)
        full_sequence += access_sequence_2

        elapsed = time.perf_counter() - start_time

        result = self.stats_snapshot(elapsed)
        result["access_sequence"] = full_sequence
        return result

    def simulate_random(self):
        self.reset()
        # this is the one test case that's actually supposed to be random
        access_sequence = generate_random_sequence(64)

        start_time = time.perf_counter()
        self.access_cache(access_sequence)
        elapsed = time.perf_counter() - start_time

        result = self.stats_snapshot(elapsed)
        # same deal as sequential: it ran twice, so double up the sequence
        # we report back, so it lines up 1:1 with trace_log
        result["access_sequence"] = access_sequence + access_sequence
        return result

    # statistics
    @property
    def total_accesses(self):
        return self.hit_count + self.miss_count

    @property
    def hit_rate(self):
        if self.total_accesses == 0:
            return 0
        return self.hit_count / self.total_accesses

    @property
    def miss_rate(self):
        if self.total_accesses == 0:
            return 0
        return self.miss_count / self.total_accesses

    @property
    def miss_penalty(self):
        # non-load-through: check cache, go to main memory, THEN read from cache again
        if self.read_policy == 0:
            return (2 * self.cache_access_time) + (self.main_memory_access_time * self.block_size)
        # load-through: check cache, then just grab the data straight from memory (faster)
        else:
            return self.cache_access_time + self.main_memory_access_time

    @property
    def average_memory_access_time(self):
        return self.hit_rate*self.cache_access_time + (self.miss_rate * self.miss_penalty)

    # actual simulated total time spent on memory accesses, based on hits/misses
    # and the configured access-time params (NOT real wall-clock time)
    @property
    def total_memory_access_time(self):
        # NLT: hits just cost (cache_access_time * block_size);
        # misses cost cache_access_time*(block_size+1) [check + read] plus the mm transfer (per block)
        if self.read_policy == 0:
            return (self.hit_count * self.cache_access_time * self.block_size
                    + self.miss_count * (self.cache_access_time * (self.block_size + 1)
                                          + self.main_memory_access_time * self.block_size))
        # LT: hits same as above; misses just cost cache_access_time plus the mm transfer (per block)
        else:
            return (self.hit_count * self.cache_access_time * self.block_size
                    + self.miss_count * (self.cache_access_time
                                          + self.main_memory_access_time * self.block_size))


# runs all 3 test cases back to back on one config and packages up the results
def run_simulation(cache_blocks, block_size, read_policy, replacement_algorithm, cache_access_time, main_memory_access_time):
    cache = CacheSimulator(
        cache_blocks,
        block_size,
        read_policy,
        replacement_algorithm,
        cache_access_time,
        main_memory_access_time,
    )

    sequential_result = cache.simulate_sequential()
    mid_repeat_result = cache.simulate_mid_repeat()
    random_result = cache.simulate_random()

    return {
        "cache_blocks": cache.cache_blocks,
        "block_size": cache.block_size,
        "read_policy": cache.read_policy,
        "replacement_algorithm": cache.replacement_algorithm,
        "cache_access_time": cache.cache_access_time,
        "main_memory_access_time": cache.main_memory_access_time,
        "test_cases": {
            "sequential": sequential_result,
            "mid_repeat": mid_repeat_result,
            "random": random_result,
        },
    }


app = Flask(__name__)
CORS(app)


# bit trick: powers of 2 only have one bit set, so value & (value-1) wipes it out to 0
def is_positive_power_of_two(value):
    return value > 1 and (value & (value - 1) == 0)


# same check but cache blocks need at least 4, per spec
def is_positive_power_of_two_min4(value):
    return value > 3 and (value & (value - 1) == 0)


@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.get_json()

    try:
        cache_blocks = int(data['cache_blocks'])
        block_size = int(data['block_size'])
        read_policy = int(data['read_policy'])
        replacement_algorithm = int(data['replacement_algorithm'])
        cache_access_time = int(data['cache_access_time'])
        main_memory_access_time = int(data['main_memory_access_time'])
    except (KeyError, TypeError, ValueError):
        return jsonify({'error': 'All fields must be filled in with valid numbers.'}), 400

    if not is_positive_power_of_two_min4(cache_blocks):
        return jsonify({'error': 'Cache Blocks must be a positive power of 2, minimum of 4 (e.g. 4, 8, 16).'}), 400

    if not is_positive_power_of_two(block_size):
        return jsonify({'error': 'Block Size must be a positive power of 2, minimum of 2 (e.g. 2, 4, 8, 16).'}), 400

    if read_policy not in (0, 1):
        return jsonify({'error': 'Read Policy must be 0 or 1.'}), 400

    if replacement_algorithm not in (0, 1):
        return jsonify({'error': 'Replacement Algorithm must be 0 or 1.'}), 400

    if cache_access_time <= 0:
        return jsonify({'error': 'Cache Access Time must be greater than 0.'}), 400

    if main_memory_access_time <= 0:
        return jsonify({'error': 'Main Memory Access Time must be greater than 0.'}), 400

    result = run_simulation(
        cache_blocks,
        block_size,
        read_policy,
        replacement_algorithm,
        cache_access_time,
        main_memory_access_time,
    )

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)