# -*- coding: utf-8 -*-
import sys
import argparse


def test(input_arg):
    print(str(input_arg))
    sys.exit(input_arg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exit', default=0)
    arg = parser.parse_args()
    test(arg)
