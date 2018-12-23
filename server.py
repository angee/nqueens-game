import os
from eventlet.green import subprocess
from flask import Flask, json, Response, request, render_template
from flask_socketio import SocketIO, emit

# setup
app = Flask(__name__)

# sockets
socketio = SocketIO(app)


@app.route('/nqueens-game')
def queensStart():
    return render_template('start.html')


@app.route('/nqueens-game', methods=['POST'])
def queensStartWithInput():
    text = request.form['N']
    processed_input = ''.join(e for e in text if e.isalnum())
    N = int(processed_input)
    # TODO: introduce proper error handling
    if N > 100:
        N = 100
    return solveQueens(N)


def solveQueens(N):
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
