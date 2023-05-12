#!/bin/bash
# Kill exact match command.
for process in $(pgrep -f "(python|python3) ./rootthebox.py --start"); do
  kill -9 $process;
done &&

# Restart
python3 ./rootthebox.py --start
