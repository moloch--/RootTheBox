#!/bin/bash 

for i in {1..4};do 
	mkdir -pv flagdirs/vgbg${i} && egrep vgbg${i} flags | cut -f2 | tee flagdirs/vgbg${i}/index.html ; 
	(python3 -m http.server -d flagdirs/vgbg${i} 808${i})& 
done
