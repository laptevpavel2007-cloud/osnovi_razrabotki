# My Awesome Lib

Calculation of personal income tax

## Installation

``bash
pip install --index-url https://test.pypi.org/simple/ ndfl_lpn


## test
from ndfl import celculate_tax

calc = celculate_tax(200_000) # == 26_000

print(f"Налог к уплате: {calc} руб.")