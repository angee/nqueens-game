"""
Server script using Flask for the N-queens game. The N-queens game has the following structure:

1. Choose the size of the chessboard (N).
2. Until all queens are placed on the chessboard:
   a. The player selects a field to place a queen on
   b. After selecting a field, the CP solver Gecode checks if a solution exists for the current selection of
      queens, using a MiniZinc model. This takes just a couple of milliseconds.
   c. If the selection is valid, then the player can continue (go to a.). Otherwise, the player can start again
      (go to 2.). ( Actually, even if the current selection is not valid, the player can place more queens or
      move some queens around and yield a correct solution ).
3. If all queens are set and the solution is valid, an animated gif will be displayed as "reward" for the player.
   There is also the option to solve the N+1 queens puzzle (go to 2. with N+1).

"""

import os

from eventlet.green import subprocess
from flask import Flask, request, render_template
from flask_socketio import SocketIO
import random

app = Flask(__name__)
socket_io = SocketIO(app)

#  Holds the column positions for the queen in the i-th row on the chess board. Set to 0 if not yet set.
queens_column_positions = []
# the dimension of the chessboard
board_size = 5
# the number of different images to display when the player has won
number_of_winning_images = 5
# the number of the image to display when the player has won
winning_image_number = 1


@app.route('/stefan')
def display_start_page_stefan():
    """
    Displays the start page before starting the game
    :return: the start page
    """
    return render_template('start.html')

@app.route('/stefan', methods=['POST'])
def play_stefan():
    """
    Displays the start page before starting the game
    :return: the start page
    """
    return play()

@app.route('/nqueens-game')
def display_start_page():
    """
    Displays the start page before starting the game
    :return: the start page
    """
    return render_template('start.html')


# After submitting the board size (after pressing 'play' button) on the initial page, start the game
@app.route('/nqueens-game', methods=['POST'])
def play():
    """
    Extracts the board size and starts the game
    :return: the first page in the game
    """
    global board_size
    text = request.form['N']
    if text == '':
        board_size = 5
    else:
        processed_input = ''.join(e for e in text if e.isalnum())
        board_size = int(processed_input)
        # Limit the board size to limit the effort for the CP solver
        if board_size > 55:
            board_size = 55
    return start_game(board_size)


@app.route('/nqueens-another-game')
def play_again():
    """
    Play the game again, on an N+1 board (where the board is slightly larger)
    :return: the queen game HTML page
    """
    global board_size
    board_size += 1
    return start_game(board_size)


@app.route('/nqueens-try-again')
def try_again():
    """
    Play the game again, with the same board size
    :return: the queen game HTML page
    """
    global board_size
    return start_game(board_size)


def start_game(chess_board_size: int):
    """
    Start playing the game, with a given board size. Initialises the queen positions (setting them all to zero),
    and other parameters for the queen game, and generates the dynamic HTML file.
    :param chess_board_size:
    :return: the queen game HTML page
    """
    global queens_column_positions
    queens_column_positions = []
    queens_column_positions[:chess_board_size] = [0] * chess_board_size  # initialise each position with zero
    arguments = {
        'queens_positions': queens_column_positions,
        'is_selection_valid': True,
        'all_queens_placed': False
    }
    return render_template('queens_state.html', **arguments)


@app.route('/select', methods=['POST'])
def select_position_of_queen():
    """
    Receives the next selected queen position and calculates the next page for the game, given the input.

    Receives the selected queen position through POST as string of the form "<column>_<row>" where <column> represents
    the column number and <row> the row number of the newly selected queen position. Then, it sets the new position
    in the global "queens_column_positions", checks if the current selection is valid, checks if the player has won,
    picks a random winning image, and creates the next HTML page in the game, depending on the given arguments.
    :return: the HTML page for the next step in the game
    """
    text = request.form['button']
    position = text.split("_")
    i = ''.join(e for e in position[0] if e.isalnum())
    j = ''.join(e for e in position[1] if e.isalnum())
    row = int(i)
    column = int(j) + 1  # account for array offset
    set_position_of_new_queen(column, row)
    arguments = {
        'queens_positions': queens_column_positions,
        'is_selection_valid': is_selection_valid(size=len(queens_column_positions)),
        'all_queens_placed': all_queens_placed(),
        'winning_image_number': pick_random_winning_image(),
    }
    return render_template('queens_state.html', **arguments)


def set_position_of_new_queen(column: int, row: int):
    """
    Updates the column position of the queen in row <row>.
    :param column:
    :param row:
    """
    global queens_column_positions
    queens_column_positions[row] = column


def is_selection_valid(size: int) -> bool:
    """
    Checks if there exists a valid solution for the currently set queens, using MiniZinc and the CP solver Gecode.

    First, it creates a MiniZinc data file, that specifies the board size N, and the currently selected queen
    positions. Then, MiniZinc is run with the data file, and if it does not print "unsatisfiable", a solution was
    found.
    :param size: the size of the board
    :return: True if a solution exists, and False otherwise.
    """
    path = os.path.dirname(os.path.realpath(__file__)) + "/minizinc/"
    create_data_file(size, path)
    with subprocess.Popen(["minizinc", "--solver", "gecode", path + "queens.mzn", "--data", path + "data.dzn"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                          universal_newlines=True) as p:
        for line in p.stdout:
            if "UNSATISFIABLE" in line:
                return False
    return True


def all_queens_placed() -> bool:
    """
    Returns True if all N queens have been placed on the chess board, False otherwise.
    :return:
    """
    global queens_column_positions
    for position in queens_column_positions:
        if position == 0: # the queen has not been placed
            return False
    return True


def create_data_file(size: int, path: str):
    """
    Creates a MiniZinc data file for finding a solution to the N-queens problem with the current placement of queens.
    :param size: the size of the chess board N
    :param path: the directory into which the data file should be written
    """
    data_file_name = path + "data.dzn"
    dzn_file = open(data_file_name, 'w')
    dzn_file.write("n = " + str(size) + ";\n")
    dzn_file.write("\n\nselected_positions = [\n")
    for position in queens_column_positions:
        dzn_file.write(str(position) + ", ")
    dzn_file.write("\n];\n")
    dzn_file.close()


def pick_random_winning_image() -> int:
    """
    Selects a random number to randomly select the next "winning image" that will be displayed when the player
    wins the game.
    :return: the random number
    """
    global winning_image_number
    global number_of_winning_images
    winning_image_number = random.randint(1, number_of_winning_images + 1)
    return winning_image_number
