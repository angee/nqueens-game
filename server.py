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
# initial chessboard size
board_size = 5


@app.route('/nqueens-game')
def queens_start():
    return render_template('start.html')


@app.route('/nqueens-game', methods=['POST'])
def play():
    text = request.form['N']
    processed_input = ''.join(e for e in text if e.isalnum())
    global board_size
    board_size = int(processed_input)
    # TODO: introduce proper error handling
    if board_size > 100:
        board_size = 100
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
        'is_valid': is_solution_valid(size=len(column_positions)),
        'has_won' : has_won()
    }
    return render_template('queens_state.html', **arguments)


def set_position(column: int, row: int):
    global column_positions
    print("setting row = " + str(row) + ", column = " + str(column))
    column_positions[row] = column
    print('[%s]' % ', '.join(map(str, column_positions)))
    return


def is_solution_valid(size: int) -> bool:
    path = os.path.dirname(os.path.realpath(__file__)) + "/minizinc/"
    problem_file_path = path + "queens.mzn"
    print(problem_file_path)
    create_data_file(size)
    os.environ["FLATZINC_CMD"] = "fzn-gecode"  # choose gecode as FlatZinc solver
    # make sure that MZN_STD_LIB_DIR is set!
    with subprocess.Popen(["minizinc", "--solver", "gecode",  problem_file_path, "--data", path + "data.dzn"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                          universal_newlines=True) as p:
        lines = []
        for line in p.stdout:
            lines.append(line)
    is_valid = True
    for line in lines:
        if "UNSATISFIABLE" in line:
            is_valid = False
    print("Solution from solving with settings: ")
    print_list(lines)
    return is_valid


def has_won():
    global column_positions
    all_positions_set = True
    for position in column_positions:
        if position == 0:
            all_positions_set = False
            break
    return all_positions_set


def create_data_file(size: int):
    path = os.path.dirname(os.path.realpath(__file__)) + "/minizinc/"
    data_file_name = path + "data.dzn"
    dzn_file = open(data_file_name, 'w')
    dzn_file.write("n = " + str(size) + ";\n")
    dzn_file.write("\n\nselected_positions = [\n")
    for position in column_positions:
        dzn_file.write(str(position) + ", ")
    dzn_file.write("\n];\n")
    dzn_file.close()
    return


def print_list(list_to_print):
    print('[%s]' % ', '.join(map(str, list_to_print)))
