# @author [Similoluwa Okunowo]
# @email [rexsimiloluwa@gmail.com]
# @create date 2021-08-25 20:30:50
# @modify date 2021-08-25 20:30:50
# @desc [Utility function for converting filesizes (integers) to Human readable bytes]

from typing import List, Union

METRIC_LABELS = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
BINARY_LABELS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]

def convert(number: Union[int, float], metric: bool=False):
    assert isinstance(number, (int, float))
    assert isinstance(metric, bool)

    unit_step = 1000 if metric else 1024
    unit_labels = METRIC_LABELS if metric else BINARY_LABELS
    if number < 0:
        number = abs(number)
    for unit in unit_labels:
        if number < unit_step:
            return "{:.2f} {}".format(number, unit)
        number /= unit_step

if __name__ == '__main__':
    print(convert(2012, True))
    print(convert(10000, True))
    print(convert(4318498233, True))
    print(convert(2000000000000000000000, True))