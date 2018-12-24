# N-queens Game

A minimal web-based application to play [N-queens](https://en.wikipedia.org/wiki/Eight_queens_puzzle),
 where the objective is to place N queens on an N x N chessboard where none of the queens may 
 attack each other.

In each step, the player selects a field on the chessboard to place a queen. After each step, 
a CP solver checks if there exists a solution for the current placement of queens.

The application uses Python [Flask](http://flask.pocoo.org/) as web-server and [MiniZinc](http://minizinc.org) 
with built-in CP solver [Gecode](http://gecode.org) for checking feasibility of the player's 
moves. 

This code was inspired by the MiniZinc web servers from 
[https://github.com/Imvoo/MiniZinc-server](https://github.com/Imvoo/MiniZinc-server).


## Installing and running the game

The application requires Python 3.6 and an installation of [MiniZinc 2.2.1](http://minizinc.org) 
(or newer). It is recommended to setup a virtual environment for Python. 
Install all required Python libraries listed in `requirements.txt` using the command 
`pip install -r requirements.txt`.

Go into your terminal and set the `$FLASK_APP` enviroment variable, for instance, under bash:

     export FLASK_APP=server.py  
     
Then run flask with the command:

     flask run
     
Finally, use your favourite browser to navigate to 
[http://localhost:5000/nqueens-game](http://localhost:5000/nqueens-game) to start playing the
 game. 
 
 
 ## Files
 
     server.py                        Flask server file
     templates/start.html             The template dynamic HTML file when starting the game
     templates/queens_state.html      The template dynamic HTML file for playing the game
     minizinc/queens.mzn              MiniZinc problem model for the N-queens problem