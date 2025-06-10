import argparse
# from PyQt5.QtWidgets import QApplication
import sys
import outdoor
from outdoor.user_interface.interface_main import run_outdoor_interface


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=str, help="log level", default="DEBUG")
    args = parser.parse_args()

    kwargs = vars(args)
    run_outdoor_interface(**kwargs)
