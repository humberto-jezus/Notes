import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    sys.path.insert(0, BASE_DIR)
    import app
