#!/bin/bash

SESSION="sudoku-solver"
STARTDIR="$(pwd)"

echo $STARTDIR

tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then
tmux new-session -d -s $SESSION 'nvim .'
tmux split-window -v 

fi

tmux attach-session -t $SESSION

