#!/bin/bash

for i in `seq 1 3`;
do
	python -B flappy.py $i &
done
