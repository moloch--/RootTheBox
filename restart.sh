#!/bin/bash
#kill exact match command. change for --start-server ;)
for process in `pgrep -f "python ./rootthebox.py -s"`;
	do echo 'Killing process ID ';
	echo $process;
	kill -9 $process;
done &&

#restart
./rootthebox.py -s
