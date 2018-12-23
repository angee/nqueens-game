% n-queens example in MiniZinc using CP techniques
% vim: ft=zinc ts=4 sw=4 et tw=0
% By Reza Rafeh July 2005
% MiniZinc version
% Peter Stuckey September 30 2006

include "alldifferent.mzn";

int: n;                                 % The number of queens.

array [1..n] of var 1..n: q;

predicate 
    noattack(int: i, int: j, var int: qi, var int: qj) =
    qi + i != qj + j /\
    qi - i != qj - j;

constraint
    forall (i in 1..n, j in i+1..n) (
        noattack(i, j, q[i], q[j])
    );

constraint alldifferent(q);

solve satisfy;

%output	["8 queens, CP version:\n"] ++
%	[	if fix(q[i]) = j then "Q " else ". " endif ++
%	 	if j = n then "\n" else "" endif
%	|	i, j in 1..n
%	];

output [ show(q[i]) ++ "\n" | i in 1..n];
