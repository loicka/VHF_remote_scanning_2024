#!/bin/bash
BASH_ENV=/home/mars/.bashrc
source /home/mars/VHF_remote_scanning_revised/env/bin/activate
cd /home/mars/VHF_remote_scanning_revised/code
python active_analysis.py
