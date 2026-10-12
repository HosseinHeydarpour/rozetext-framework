import os
import subprocess

def test_open(target_path):
    norm_p = os.path.normpath(os.path.abspath(target_path.replace("/", "\\")))
    print("Testing open on:", norm_p)
    if os.path.isfile(norm_p):
        folder = os.path.dirname(norm_p)
        print("Opening folder with os.startfile:", folder)
        os.startfile(folder)
        cmd = f'explorer.exe /select,"{norm_p}"'
        print("Running select:", cmd)
        subprocess.Popen(cmd, shell=True)
        return True
    elif os.path.isdir(norm_p):
        print("Opening dir with os.startfile:", norm_p)
        os.startfile(norm_p)
        return True
    return False

test_open(r"d:\rozetext-framework\downloads\reels\2026-10-04\2026-10-04_Slot-05_DZQJRhRNpQG_audio.mp3")
