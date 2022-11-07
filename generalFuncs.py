
# general functions

import readline
import os

# ===============================================
def prefilledInput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()

# ===============================================

def SaveFile(fnuse, mode, tx):

    file1 = open(fnuse, mode)
    file1.write(tx+"\n")
    file1.close()     
    
# ===============================================
