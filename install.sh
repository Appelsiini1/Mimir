#!/bin/bash

# Python dependencies
# run only with -p
if [[ $1 -eq '-p']]
then
    pip install dearpygui
    pip install whoosh
fi

# Other dependencies
sudo apt update
sudo apt install texlive
sudo apt install python3-pygments