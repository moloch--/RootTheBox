#!/bin/bash
# Kill exact match command.
for process in $(pgrep -f "python ./rootthebox.py (-s|--start-server)"); do
  kill -9 $process;
done &&

# Restart
./rootthebox.py -s
