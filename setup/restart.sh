#!/bin/bash
# Kill exact match command. TODO: match both --start-server and -s ;)
for process in `pgrep -f "python ./rootthebox.py -s"`;
  do kill -9 $process;
done &&

# Restart
./rootthebox.py -s