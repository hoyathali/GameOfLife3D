# 3D Game of Life


Welcome to the 3D Game of Life project! This implementation provides an interactive visualization of Conway's Game of Life in a 3D space using Mayavi.

## Basic Rules of the Game
The rules of the Game of Life 3D are an extension of the classic Game of Life rules into three dimensions. Here are the key points:

1. **Birth and Survival:** A cell in the 3D grid is "born" if it has exactly a certain number of live neighbors, similar to the 2D version. Additionally, a live cell survives to the next generation if it has a specific number of live neighbors.

2. **Neighborhood Definition:** In the 3D version, each cell has 26 neighbors, accounting for all adjacent cells in the three dimensions (including diagonals).

3. **Overpopulation and Underpopulation:** If a live cell has too few (underpopulation) or too many (overpopulation) live neighbors, it dies due to isolation or overcrowding, respectively.

4. **Birth Conditions:** A cell becomes alive in the next generation if it is currently dead and has a specific number of live neighbors, simulating reproduction.

5. **Static and Oscillating Patterns:** The Game of Life 3D, like its 2D counterpart, can exhibit static patterns where cells remain unchanged, or oscillating patterns where cells alternate between different states over generations, providing dynamic and evolving structures in the three-dimensional space.


## Getting Started

Follow these steps to run the code and explore the 3D Game of Life:

### Prerequisites

- Python installed on your system
- GPU for optimal performance

## Running the Code
1. Clone the Repository onto a system with GPU.
2. Pip install all the required libraries (requirements.txt) ( pip install numba mayavi numpy flask flask-socketio requests )
3. Run `python main.py` which will launch a Mayavi visualization window. This will launch a Mayavi window, providing an interactive visualization of the generations.
4. Run `python servermain.py` on a system with GPU as this has the kernel code. If you are running these two files on different systems, please update `servermain.py` file, line 77, with the public URL to your system where `main.py` is running:
   ```python
   url = 'http://localhost:5000/receive'
5. That’s it we have our 3D Game of Life Ready. 


# Evaluation

## Comparison Report: GPU vs. CPU Execution

**Objective:**
To compare the execution times of a specific task with and without GPU acceleration. We have performed many tests with different sizes of worlds, starting from (10*10*10) to (100*100*100).

### Run 1: Without GPU (30 30 30 - Average time for a Generation)
- **Execution Time:** 0.000773030098 seconds 

### Run 2: With GPU (30 30 30 - Average time for a Generation)
- **Execution Time:** 0.0004838885683 seconds

### Comparison:
The execution time with GPU acceleration (Run 2) is approximately 37.5% smaller than without GPU acceleration (Run 1). This reduction in execution time suggests that utilizing GPU resources has led to a performance improvement for the given task.
