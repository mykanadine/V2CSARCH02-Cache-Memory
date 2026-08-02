from flask import Flask, jsonify, request
from flask_cors import CORS
from cache_simulator import run_simulation

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
