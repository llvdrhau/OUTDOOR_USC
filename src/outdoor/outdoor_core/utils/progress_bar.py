
import sys
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    This function prints a progress bar in the console. It is used in the outdoor_core.utils.progress_bar module.
    :param iteration: current iteration (Int)
    :param total: total iterations (Int)
    :param prefix: prefix string (Str)
    :param suffix: suffix string (Str)
    :param decimals: positive number of decimals in percent complete (Int)
    :param length: character length of bar (Int)
    :param fill: bar fill character (Str)
    :param printEnd: end character (e.g. "\r", "\r\n") (Str)
    :return: None
    """
    # Source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    # Now let's print the progress bar
    progress = (iteration + 1) / total
    bar_length = 40  # Modify this to change the length of the progress bar
    block = int(round(bar_length * progress))
    text = "\r{2} Progress {3}: [{0}] {1:.2f}%".format("#" * block + "-" * (bar_length - block), progress * 100, prefix, suffix)
    sys.stdout.write(text)
    sys.stdout.flush()
