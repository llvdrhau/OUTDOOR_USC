import time


def time_printer(passed_time=None, programm_step=None, printTimer=True):


    if passed_time is None:
        timer = time.time()
        if printTimer:
            print(f'--INFO:-- Start: {programm_step} ----')
    else:
        timer = time.time() - passed_time
        if printTimer:
            print(f"--INFO:-- Finished: {programm_step} ----")
            print(f"--INFO:-- Time: {round(timer,2)} sec ----")
    return timer
