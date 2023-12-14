from numba import cuda
import numpy as np
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import threading

DIM_X, DIM_Y, DIM_Z = 10, 10, 10

@cuda.jit
def kernel_update_conways_game_of_life(current_state, next_state):
    i, j, k = cuda.grid(3)
    dim_x, dim_y, dim_z = current_state.shape
    if 0 <= i < dim_x and 0 <= j < dim_y and 0 <= k < dim_z:
        alive_neighbors = 0
        for di in range(-1, 2):
            for dj in range(-1, 2):
                for dk in range(-1, 2):
                    ni, nj, nk = i + di, j + dj, k + dk
                    if 0 <= ni < dim_x and 0 <= nj < dim_y and 0 <= nk < dim_z:
                        alive_neighbors += current_state[ni, nj, nk]

        alive_neighbors -= current_state[i, j, k]
        if current_state[i, j, k] == 1:
            next_state[i, j, k] = 1 if 1 <= alive_neighbors <= 4 else 0
        else:
            next_state[i, j, k] = 1 if alive_neighbors == 3 else 0



def update_matrix_gpu(current_generation, next_generation):
    threadsperblock = (8, 8, 8)
    blockspergrid_x = (DIM_X + threadsperblock[0] - 1) // threadsperblock[0]
    blockspergrid_y = (DIM_Y + threadsperblock[1] - 1) // threadsperblock[1]
    blockspergrid_z = (DIM_Z + threadsperblock[2] - 1) // threadsperblock[2]
    blockspergrid = (blockspergrid_x, blockspergrid_y, blockspergrid_z)
    # Create CUDA streams
    stream_copy = cuda.stream()
    stream_kernel = cuda.stream()
    kernel_update_conways_game_of_life[blockspergrid, threadsperblock, stream_kernel](
        current_generation, next_generation
    )

def get_next_generation(current_generation):
    next_generation = np.empty_like(current_generation)

    # Create CUDA streams
    stream_copy = cuda.stream()
    stream_kernel = cuda.stream()
    # Allocate device memory for current and next generations
    start_time = time.time()
    #--------------------------------------------------------------------------------------------------------------------------------------
    current_generation_device = cuda.to_device(current_generation, stream=stream_copy)
    next_generation_device = cuda.to_device(next_generation, stream=stream_copy)
    # Launch kernel in stream_kernel
    update_matrix_gpu(current_generation_device, next_generation_device)
    # Copy data from device to host using stream_copy
    next_generation_device.copy_to_host(next_generation, stream=stream_copy)
    # Synchronize streams to ensure all operations are completed
    cuda.synchronize()
    #--------------------------------------------------------------------------------------------------------------------------------------
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print("Generation Calculated:", elapsed_time, "seconds\n")
    return next_generation

def generate_pulsar_pattern():
    size=DIM_X
    pulsar = np.zeros((size, size, size), dtype=np.int8)
    
    # Define the pulsar pattern centered in the array
    center = size // 2
    pulsar[center - 1:center + 2, center - 2:center + 3, center - 1] = 1
    pulsar[center - 1:center + 2, center - 2:center + 3, center + 1] = 1
    pulsar[center - 1:center + 2, center - 2:center + 3, center - 3] = 1
    pulsar[center - 1:center + 2, center - 2:center + 3, center + 3] = 1

    return pulsar

def generate_glider_pattern():
    size=DIM_X
    glider = np.zeros((size, size, size), dtype=np.int8)

    # Define the glider pattern
    glider[1, 0, 0] = 1
    glider[2, 1, 0] = 1
    glider[0:3, 2, 0] = 1

    return glider

def generate_corner_to_center_pattern():
    size=DIM_X
    pattern = np.zeros((size, size, size), dtype=np.int8)

    # Diagonal lines from top-left corner
    for i in range(size):
        pattern[i, i, 0] = 1

    # Diagonal lines from top-right corner
    for i in range(size):
        pattern[i, size - i - 1, 0] = 1

    # Diagonal lines from bottom-left corner
    for i in range(size):
        pattern[size - i - 1, i, 0] = 1

    # Diagonal lines from bottom-right corner
    for i in range(size):
        pattern[size - i - 1, size - i - 1, 0] = 1

    return pattern

def generate_challenging_pattern():
    size=DIM_X
    pattern = np.zeros((size, size, size), dtype=np.int8)

    # Add a central core
    center = size // 2
    pattern[center - 1:center + 2, center - 1:center + 2, center - 1:center + 2] = 1

    # Add diagonal lines radiating from the core
    pattern[center - 3:center + 4, center - 3:center + 4, center - 3] = 1
    pattern[center - 3:center + 4, center - 3:center + 4, center + 3] = 1


    return pattern

def generate_moving_pattern():
    size=DIM_X
    pattern = np.zeros((size, size, size), dtype=np.int8)

    # Glider moving from top-left to bottom-right
    pattern[0:3, 0:3, 0] = 1

    # Glider moving from bottom-left to top-right
    pattern[size-3:size, 0:3, 0] = 1

    # Glider moving from top-right to bottom-left
    pattern[0:3, size-3:size, 0] = 1

    # Glider moving from bottom-right to top-left
    pattern[size-3:size, size-3:size, 0] = 1

    return pattern

def send_message(matrix):
    url = 'http://localhost:5000/receive'
    matrix_list = matrix.tolist()
    data = {'message': matrix_list}
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.post(url, json=data, verify=False)
    if response.status_code == 200:
        print("Matrix sent successfully to System B")
    else:
        print("Failed to send matrix to System B")
        print(response.status_code)

def send_matrices_continuously():
    initial_state = generate_pulsar_pattern()
    #initial_state = generate_glider_pattern()
    #initial_state = generate_corner_to_center_pattern()
    #initial_state = generate_challenging_pattern()
    #initial_state = generate_moving_pattern()

    send_message(initial_state)
    matrix_to_send=initial_state.copy()
    i=10
    while i>0:
        # Get the next generation using the function from gol_numba.py
        next_generation_matrix = get_next_generation(matrix_to_send)
        matrix_to_send=next_generation_matrix
        # Send the next generation matrix
        send_message(next_generation_matrix)
        i=i-1
        time.sleep(1)


if __name__ == '__main__':
    # Start sending matrices in a separate thread
    thread = threading.Thread(target=send_matrices_continuously)
    thread.start()
    # Keep the main thread running to allow interruption
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping matrix sending.")
