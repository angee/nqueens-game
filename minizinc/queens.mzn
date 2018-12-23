% n-queens example in MiniZinc using CP techniques
% vim: ft=zinc ts=4 sw=4 et tw=0
% By Reza Rafeh July 2005
% MiniZinc version
% Peter Stuckey September 30 2006
% modified by Andrea Rendl, December 2018.

include "alldifferent.mzn";

int: n;                                 % The number of queens.
array [1..n] of 0..n: selected_positions;  % Preselected positions

array [1..n] of var 1..n: q;

predicate 
    noattack(int: i, int: j, var int: qi, var int: qj) =
    qi + i != qj + j /\
    qi - i != qj - j;

constraint
   forall (i in 1..n) (
       selected_positions[i] > 0 -> q[i] = selected_positions[i]
   );

constraint
    forall (i in 1..n, j in i+1..n) (
        noattack(i, j, q[i], q[j])
    );

constraint alldifferent(q);

solve satisfy;

output [ show(q[i]) ++ "\n" | i in 1..n];
