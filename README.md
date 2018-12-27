# N-queens Game

A minimal web-based application to play [N-queens](https://en.wikipedia.org/wiki/Eight_queens_puzzle),
 where the objective is to place N queens on an N x N chessboard where none of the queens may 
 attack each other.

In each step, the player selects a field on the chessboard to place a queen. After each step, 
a CP solver checks if there exists a solution for the current placement of queens.


![alt text](http://andrearendl.com/nqueens.png "Playing the 5-games puzzle")


The application uses Python [Flask](http://flask.pocoo.org/) as web-server and [MiniZinc](http://minizinc.org) 
with built-in CP solver [Gecode](http://gecode.org) for checking feasibility of the player's 
moves. 

This code was inspired by the MiniZinc web servers from 
[https://github.com/Imvoo/MiniZinc-server](https://github.com/Imvoo/MiniZinc-server).


## Installation instructions

The application requires Python 3.5 (or higher) and it is recommended to setup a virtual 
environment for Python. Install all required Python libraries listed in `requirements.txt` 
using the command the `pip install -r requirements.txt` in your terminal. 

You will also need to install [MiniZinc 2.2.1](http://minizinc.org) (or a newer version).
After downloading the binary bundle, make sure that `minizinc` is in your path. You can 
test this by typing `minizinc` into your terminal and check if the program can be executed. 
To achive this under Linux, you will first need to add MiniZinc's `bin/`directory 
to your the `$PATH` environment variable, and add MiniZinc's `lib/` directory to 
`LD_LIBRARY_PATH`:

    export PATH=$PATH:/path/to/minizinc/bin
    export LD_LIBRARY_PATH=/path/to/minizinc/lib/:$LD_LIBRARY_PATH

## Running the game on your local machine

To run the game on your localhost, open a terminal, enter your Python virtual enviroment if 
have set it up, and set the `$FLASK_APP` environment variable:

     export FLASK_APP=server.py  
     
Then run flask with the command:

     flask run
     
Finally, use your favourite browser to navigate to 
[http://localhost:5000/nqueens-game](http://localhost:5000/nqueens-game) to start playing the
 game. 
 
 
 ## Files
 
     LICENSE                          the software license
     requirements.txt                 the file containing the required Python libraries                       
     server.py                        Flask server file
     templates/start.html             The template dynamic HTML file when starting the game
     templates/queens_state.html      The template dynamic HTML file for playing the game
     minizinc/queens.mzn              MiniZinc problem model for the N-queens problem