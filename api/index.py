import time
import random

from flask import Flask, jsonify, request
from flask_cors import CORS

MAIN_MEMORY = 1024


def generate_random_sequence(accesses):
    sequence = []
    for _ in range(accesses):
        sequence.append(random.randint(0, 1023))

    return sequence


class CacheSimulator:
    def __init__(self, cache_blocks, block_size, read_policy, replacement_algorithm, cache_access_time, main_memory_access_time):
        self.cache_blocks = cache_blocks
        self.block_size = block_size
        self.cache = [None] * self.cache_blocks
        self.miss_count = 0
        self.hit_count = 0
        self.read_policy = read_policy  # NLT (0) OR LT (1)
        self.replacement_algorithm = replacement_algorithm  # LRU (0) OR MRU (1)
        self.cache_access_time = cache_access_time
        self.main_memory_access_time = main_memory_access_time
        self.counter = [None] * self.cache_blocks
        self.view = False  # False = final snapshot, True = step-by-step

    def cache_hit(self, ctr, block):
        print(f"HIT -> {block}")  # for debugging
        idx = self.cache.index(block)
        self.counter[idx] = ctr
        self.hit_count += 1

    def cache_miss(self, ctr, block):
        if None in self.cache:
            idx = self.cache.index(None)

        # use replacement algorithm
        else:
            idx = self.replace_block()

        self.cache[idx] = block
        self.counter[idx] = ctr
        self.miss_count += 1
        print(f"MISS -> {block}")

    def replace_block(self):
        # LRU
        if self.replacement_algorithm == 0:
            return self.counter.index(min(self.counter))  # get the index of the smallest number in the counter
        # MRU
        else:
            return self.counter.index(max(self.counter))  # get the index of the largest number in counter

    def access_cache(self, access_sequence):
        for ctr, block in enumerate(access_sequence):
            # cache hit
            if block in self.cache:
                self.cache_hit(ctr, block)

            # cache miss
            elif block not in self.cache:
                self.cache_miss(ctr, block)

    def display_cache(self, time):
        print(f'Final Cache: {self.cache}')
        print(f'Total Access Count: {self.total_accesses}')
        print(f'Cache Hit: {self.hit_count}')
        print(f'Cache Miss: {self.miss_count}')
        print(f'Hit rate: {self.hit_rate}')
        print(f'Miss rate: {self.miss_rate}')
        print(f'Average Memory Access Time: {self.average_memory_access_time}')
        print(f'Total Memory Access Time: {time}')

    # --- TEST CASES ---

    def simulate_sequential(self):
        access_sequence = generate_random_sequence(self.cache_blocks * 2)
        print(f'Access Sequence: {access_sequence}')
        start_time = time.time()
        self.access_cache(access_sequence)
        self.access_cache(access_sequence)
        end_time = time.time() - start_time
        self.display_cache(end_time)

    def simulate_mid_repeat(self):
        access_sequence_1 = []
        access_sequence_2 = []

        # block 0 to n-1
        for i in range(self.cache_blocks - 1):
            access_sequence_1.append(i)

        # block 0 to 2n-1
        for i in range((self.cache_blocks * 2) - 1):
            access_sequence_2.append(i)

        start_time = time.time()

        self.access_cache(access_sequence_1)

        self.access_cache(access_sequence_2)
        self.access_cache(access_sequence_2)

        access_sequence_1.reverse()
        self.access_cache(access_sequence_1)

        access_sequence_2.reverse()
        self.access_cache(access_sequence_2)
        self.access_cache(access_sequence_2)

        end_time = time.time() - start_time
        self.display_cache(end_time)

    def simulate_random(self):
        access_sequence = generate_random_sequence(64)
        start_time = time.time()
        self.access_cache(access_sequence)
        self.access_cache(access_sequence)
        end_time = time.time() - start_time
        self.display_cache(end_time)

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
        # NLT
        if self.read_policy == 0:
            return (2 * self.cache_access_time) + (self.main_memory_access_time * self.cache_blocks)  # initial cache check + mm access time + cache read
        # LT
        else:
            return self.cache_access_time + self.main_memory_access_time  # initial cache check + transfer data address

    @property
    def average_memory_access_time(self):
        return self.hit_rate + (self.miss_rate * self.miss_penalty)


def run_simulation(cache_blocks, block_size, read_policy, replacement_algorithm, cache_access_time, main_memory_access_time):
    cache = CacheSimulator(
        cache_blocks,
        block_size,
        read_policy,
        replacement_algorithm,
        cache_access_time,
        main_memory_access_time,
    )

    cache.simulate_sequential()
    cache.simulate_mid_repeat()
    cache.simulate_random()

    return {
        "cache_blocks": cache.cache_blocks,
        "block_size": cache.block_size,
        "hit_count": cache.hit_count,
        "miss_count": cache.miss_count,
        "total_accesses": cache.total_accesses,
        "hit_rate": cache.hit_rate,
        "miss_rate": cache.miss_rate,
        "average_memory_access_time": cache.average_memory_access_time,
        "final_cache_state": cache.cache,
    }


app = Flask(__name__)
CORS(app)


def is_positive_power_of_two(value):
    return value > 0 and (value & (value - 1) == 0)


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

    if not is_positive_power_of_two(cache_blocks):
        return jsonify({'error': 'Cache Blocks must be a positive power of 2 (e.g. 4, 8, 16).'}), 400

    if not is_positive_power_of_two(block_size):
        return jsonify({'error': 'Block Size must be a positive power of 2 (e.g. 4, 8, 16).'}), 400

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
