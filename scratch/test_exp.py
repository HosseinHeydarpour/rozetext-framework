import os
import subprocess

path = r'd:\rozetext-framework\downloads\reels\DP9UfRmCOru\DP9UfRmCOru_audio.mp3'
abs_p = os.path.abspath(path)

# Test 1: string command via shell=True
cmd_str = f'explorer.exe /select,"{abs_p}"'
print('Running:', cmd_str)
p = subprocess.Popen(cmd_str, shell=True)
print('Popen return/pid:', p.pid)

# Test 2: os.startfile on folder
folder = os.path.dirname(abs_p)
print('Folder:', folder)
os.startfile(folder)
print('os.startfile succeeded!')
