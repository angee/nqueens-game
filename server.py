import os
from eventlet.green import subprocess
from flask import Flask, json, Response, request, render_template
from flask_socketio import SocketIO, emit

# setup
app = Flask(__name__)

# sockets
socket_io = SocketIO(app)

#  Holds the column positions for the queen in the i-th row on the chess board. Set to 0 if not yet set.
column_positions = []
# the dimension of the chessboard
board_size = 5


@app.route('/riccardo-xmas')
def queens_start():
    return render_template('start.html')


@app.route('/riccardo-xmas', methods=['POST'])
def play():
    global board_size
    text = request.form['N']
    if text == '':
        board_size = 5
    else:
        processed_input = ''.join(e for e in text if e.isalnum())
        board_size = int(processed_input)
    # Do not allow board sizes larger than 55
    if board_size > 55:
        board_size = 55
    return play(board_size)


@app.route('/nqueens-another-game')
def play_again():
    global board_size
    board_size += 1
    return play(board_size)


@app.route('/nqueens-try-again')
def try_again():
    global board_size
    return play(board_size)


def play(chess_board_size: int):
    global column_positions
    column_positions = []
    column_positions[:chess_board_size] = [0] * chess_board_size  # initialise each position with zero
    arguments = {
        'queens_positions': column_positions,
        'is_valid': True,
        'has_won': False
    }
    return render_template('queens_state.html', **arguments)


@app.route('/select', methods=['POST'])
def select_position_of_queen():
    text = request.form['button']
    position = text.split("_")
    i = ''.join(e for e in position[0] if e.isalnum())
    j = ''.join(e for e in position[1] if e.isalnum())
    row = int(i)
    column = int(j) + 1  # account for array offset
    set_position_of_new_queen(column, row)
    arguments = {
        'queens_positions': column_positions,
        'is_valid': is_solution_valid(size=len(column_positions)),
        'has_won': has_won()
    }
    return render_template('queens_state.html', **arguments)


def set_position_of_new_queen(column: int, row: int):
    global column_positions
    column_positions[row] = column
    return


def is_solution_valid(size: int) -> bool:
    path = os.path.dirname(os.path.realpath(__file__)) + "/minizinc/"
    create_data_file(size, path)
    # make sure that MZN_STD_LIB_DIR is set!
    with subprocess.Popen(["minizinc", "--solver", "gecode", path + "queens.mzn", "--data", path + "data.dzn"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                          universal_newlines=True) as p:
        for line in p.stdout:
            if "UNSATISFIABLE" in line:
                return False
    return True


def has_won() -> bool:
    global column_positions
    for position in column_positions:
        if position == 0:
            return False
    return True


def create_data_file(size: int, path: str):
    data_file_name = path + "data.dzn"
    dzn_file = open(data_file_name, 'w')
    dzn_file.write("n = " + str(size) + ";\n")
    dzn_file.write("\n\nselected_positions = [\n")
    for position in column_positions:
        dzn_file.write(str(position) + ", ")
    dzn_file.write("\n];\n")
    dzn_file.close()
    return
