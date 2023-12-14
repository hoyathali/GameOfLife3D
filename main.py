import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import threading
import numpy as np
from mayavi import mlab
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Set the logging level for Werkzeug (used by Flask-SocketIO) to ERROR
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

# Initialize Mayavi scene
scene = mlab.figure(figure='GameOfLife', bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(800, 600))

def update_message(matrix):
    # Callback function to update the 3D matrix plot
    plot_3d_matrix(matrix)

@socketio.on('update_zoom', namespace='/')
def update_zoom():
    # Callback function to update the zoom parameters
    azimuth, elevation, distance = mlab.view()
    socketio.emit('update_zoom', {'azimuth': azimuth, 'elevation': elevation, 'distance': distance}, namespace='/')

def plot_3d_matrix(matrix):
    # Clear the scene
    mlab.clf(figure=scene)

    # Calculate grid indices for 1 values
    x, y, z = np.where(matrix == 1)

    # Plot points and bounding cube
    points = mlab.points3d(x, y, z, scale_factor=0.8, color=(0, 0, 1), opacity=1)
    outline = mlab.outline(extent=[0, matrix.shape[0], 0, matrix.shape[1], 0, matrix.shape[2]])

    # Calculate grid indices for 0 values
    x_zero, y_zero, z_zero = np.where(matrix == 0)
    points_zero = mlab.points3d(x_zero, y_zero, z_zero, scale_factor=0.8, color=(1, 1, 1), opacity=0.05)

@app.route('/receive', methods=['POST'])
def receive_message():
    if request.method == 'POST':
        # Handling POST requests
        data = request.get_json()

        # Convert the received message to a NumPy array
        matrix = np.array(data['message'])

        # Emit the message to the connected clients
        socketio.emit('update_message', matrix.tolist(), namespace='/')

        # Perform any additional action based on the received message
        update_message(matrix)

        return jsonify({'status': 'Message received successfully'})

def run_flask_server():
    # Function to run the Flask server
    socketio.run(app, debug=True, host='0.0.0.0', use_reloader=False)

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask_server)
flask_thread.start()

# Periodically store the current zoom parameters
def store_current_zoom():
    while True:
        time.sleep(0.1)  # Adjust the interval as needed
        socketio.emit('update_zoom', namespace='/')  # Emit signal to update zoom parameters

# Start the zoom storage thread
zoom_thread = threading.Thread(target=store_current_zoom)
zoom_thread.start()

# Start the Mayavi main loop
mlab.show()
