import argparse
# from PyQt5.QtWidgets import QApplication
import sys
import outdoor
from outdoor.user_interface.main2 import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=str, help="log level", default="DEBUG")
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
