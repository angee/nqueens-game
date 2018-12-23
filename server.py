import os
from eventlet.green import subprocess
from flask import Flask, json, Response, request, render_template
from flask_socketio import SocketIO, emit

# setup
app = Flask(__name__)

# sockets
socketio = SocketIO(app)

# positions of the queens
column_positions = []
# set to True if the positions have been initialised
initialised_positions = False


@app.route('/nqueens-game')
def queensStart():
    return render_template('start.html')


@app.route('/nqueens-game', methods=['POST'])
def set_chessboard_size():
    text = request.form['N']
    processed_input = ''.join(e for e in text if e.isalnum())
    board_size = int(processed_input)
    # TODO: introduce proper error handling
    if board_size > 100:
        board_size = 100
    global column_positions
    column_positions[:board_size] = [0] * board_size  # initialise each position with zero
    arguments = {
        'queens_positions': column_positions,
    }
    global initialised_positions
    initialised_positions = True
    return render_template('queens_state.html', **arguments)


@app.route('/select', methods=['POST'])
def select_position_of_queen():
    text = request.form['button']
    print("text = " + text)
    position = text.split("_")
    i = ''.join(e for e in position[0] if e.isalnum())
    j = ''.join(e for e in position[1] if e.isalnum())
    row = int(i)
    column = int(j) + 1  # account for array offset
    # set the position of the selected queen
    set_position(column, row)
    arguments = {
        'queens_positions': column_positions,
    }
    return render_template('queens_state.html', **arguments)


def set_position(column: int, row: int):
    global column_positions
    print("setting row = " + str(row) + ", column = " + str(column))
    column_positions[row] = column
    print('[%s]' % ', '.join(map(str, column_positions)))
    return


@app.route('/solve', methods=['POST'])
def start_solving_queens():
    text = request.form['N']
    processed_input = ''.join(e for e in text if e.isalnum())
    N = int(processed_input)
    # TODO: introduce proper error handling
    if N > 100:
        N = 100
    column_positions[:N] = [0] * N
    return solve_queens(N)


def solve_queens(N):
    path = os.path.dirname(os.path.realpath(__file__)) + "/minizinc/"
    problem_file_path = path + "queens.mzn"
    print(problem_file_path)
    os.environ["FLATZINC_CMD"] = "fzn-gecode"  # choose gecode as FlatZinc solver
    # make sure that MZN_STD_LIB_DIR is set!
    with subprocess.Popen(["minizinc", "--solver", "gecode", problem_file_path, "-D n=" + str(N) + ";"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                          universal_newlines=True) as p:

        lines = []
        for line in p.stdout:
            lines.append(line)

    queen_positions = []
    for i in range(0, len(lines) - 1):  # ignore the last line which is just a bar
        trimmed_line = ''.join(e for e in lines[i] if e.isalnum())  # remove everything that is not a number
        queen_positions.append(int(trimmed_line))

    arguments = {
        'queens_positions': queen_positions,
    }
    return render_template('queens_solution.html', **arguments)
