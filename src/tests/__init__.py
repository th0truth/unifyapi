import pathlib
import sys
from pprint import pprint

# print("dd")

# sys.path.append("../app")
sys.path.append(str(pathlib.Path(__file__).parent.parent) + "/app")


pprint(sys.path)

# sys.path.append(str(pathlib.Path(__file__).parent))