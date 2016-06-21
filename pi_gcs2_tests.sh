#!/bin/bash

export PYTHONPATH=.:$PYTHONPATH
python -m unittest discover -p "*_test.py" -v
