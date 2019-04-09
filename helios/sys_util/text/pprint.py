#  -*- coding: UTF8 -*-

from __future__ import print_function


def print_error(str): print('\033[91m {}\033[00m'.format(str))


def print_info(str): print('\033[95m {}\033[00m'.format(str))


def print_success(str): print('\033[92m {}\033[00m'.format(str))


def print_spaceship(): print('\xF0\x9F\x9A\x80', end=' ')


def print_warn(str): print('\033[94m {}\033[00m'.format(str))
