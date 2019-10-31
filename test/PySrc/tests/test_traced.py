import sys

import pytest

from space_tracer.main import TraceRunner, replace_input
from test_code_tracer_main import EXAMPLE_DRIVER_PATH, EXAMPLE_PRINTING_PATH
from test_report_builder import trim_report


def test_one_function():
    code = """\
from space_tracer import traced


@traced
def foo(n):
    s = 'x'
    for i in range(n):
        s += 'y'
    return s


def bar(num):
    s = 'a'
    for i in range(num):
        s += 'b'
    return s


print(foo(3))
print(bar(3))
"""
    expected_report = """\
    @traced                |
    def foo(n):            | n = 3
        s = 'x'            | s = 'x'
        for i in range(n): | i = 0    | i = 1     | i = 2
            s += 'y'       | s = 'xy' | s = 'xyy' | s = 'xyyy'
        return s           | return 'xyyy' """

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--source_indent', '4',
            '--traced_file', 'example.py',
            'example.py'])

    assert trim_report(expected_report) == trim_report(report)


def test_two_functions():
    code = """\
from space_tracer import traced


@traced
def foo(n):
    s = 'x'
    for i in range(n):
        s += 'y'
    return s


@traced
def bar(num):
    s = 'a'
    for i in range(num):
        s += 'b'
    return s


print(foo(3))
print(bar(3))
"""
    expected_report = """\
    @traced                  |
    def foo(n):              | n = 3
        s = 'x'              | s = 'x'
        for i in range(n):   | i = 0    | i = 1     | i = 2
            s += 'y'         | s = 'xy' | s = 'xyy' | s = 'xyyy'
        return s             | return 'xyyy'
    @traced                  |
    def bar(num):            | num = 3
        s = 'a'              | s = 'a'
        for i in range(num): | i = 0    | i = 1     | i = 2
            s += 'b'         | s = 'ab' | s = 'abb' | s = 'abbb'
        return s             | return 'abbb'
"""

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--source_indent', '4',
            '--traced_file', 'example.py',
            'example.py'])

    assert trim_report(expected_report) == trim_report(report)


def test_command_line():
    """ Specify a traced method with command-line option --traced. """
    code = """\
def foo(n):
    s = 'x'
    for i in range(n):
        s += 'y'
    return s


def bar(num):
    s = 'a'
    for i in range(num):
        s += 'b'
    return s


print(foo(3))
print(bar(3))
"""
    expected_report = """\
def bar(num):            | num = 3
    s = 'a'              | s = 'a'
    for i in range(num): | i = 0    | i = 1     | i = 2
        s += 'b'         | s = 'ab' | s = 'abb' | s = 'abbb'
    return s             | return 'abbb'"""

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--traced', '__main__.bar',
            '--traced_file', 'example.py',
            'example.py'])

    assert expected_report == report


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="Can't tell which file to load source code from before 3.0.")
def test_without_traced_file():
    expected_report = """\
def foo(x):                       | x = 42
    return x + 1                  | return 43
                                  |
                                  |
def bar(bucket):                  |
    bucket.add('bar')             |
                                  |
                                  |
if __name__ == '__live_coding__': |
    y = foo(3)                    |"""

    report = TraceRunner().trace_command([
        'space_tracer',
        '--traced', 'example_source',
        EXAMPLE_DRIVER_PATH])

    assert expected_report == report


def test_default_traced():
    expected_report = """\
from __future__ import print_function   |
                                        |
                                        |
def custom_print(text, suffix):         | text = 'Hello, example' | suffix = '!'
    print(text + suffix)                | print('Hello, example!')
                                        |
                                        |
if __name__ == '__main__':              |
    custom_print('Hello, example', '!') |"""

    report = TraceRunner().trace_command([
        'space_tracer',
        EXAMPLE_PRINTING_PATH])

    assert expected_report == report


def test_traced_main_without_traced_file():
    expected_report = """\
def custom_print(text, suffix): | text = 'Hello, example' | suffix = '!'
    print(text + suffix)        | print('Hello, example!')"""

    report = TraceRunner().trace_command([
        'space_tracer',
        '--traced=__main__.custom_print',
        EXAMPLE_PRINTING_PATH])

    assert expected_report == report


def test_traced_function():
    code = """\
def foo(n):
    return n + 1

def bar(n):
    return n - 1

foo(10)
bar(20)
"""
    expected_report = """\
def bar(n):      | n = 20
    return n - 1 | return 19"""

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--traced=bar',
            '--traced_file', 'example.py',
            'example.py'])

    assert expected_report == report


def test_other_decorator():
    """ Other decorators shouldn't affect tracing. """
    code = """\
from __future__ import print_function
class Foo(object):
    def foo(self, x):
        return x + 1
    
    @staticmethod
    def bar(x):
        return x + 2

f = Foo()
print(f.foo(10))
print(f.bar(20))
"""
    expected_report = """\
from __future__ import print_function |
class Foo(object):                    |
    def foo(self, x):                 | x = 10
        return x + 1                  | return 11
                                      |
    @staticmethod                     |
    def bar(x):                       | x = 20
        return x + 2                  | return 22
                                      |
f = Foo()                             |
print(f.foo(10))                      | print('11')
print(f.bar(20))                      | print('22')"""

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--traced_file', 'example.py',
            'example.py'])

    assert expected_report == report


def test_attribute_decorator():
    """ The decorator is a module attribute. """
    code = """\
from __future__ import print_function
class Foo(object):
    def foo(self, x):
        return x + 1
    
    @__builtins__.staticmethod
    def bar(x):
        return x + 2

f = Foo()
print(f.foo(10))
print(f.bar(20))
"""
    expected_report = """\
from __future__ import print_function |
class Foo(object):                    |
    def foo(self, x):                 | x = 10
        return x + 1                  | return 11
                                      |
    @__builtins__.staticmethod        |
    def bar(x):                       | x = 20
        return x + 2                  | return 22
                                      |
f = Foo()                             |
print(f.foo(10))                      | print('11')
print(f.bar(20))                      | print('22')"""

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--traced_file', 'example.py',
            'example.py'])

    assert expected_report == report


def test_one_function_live_mode():
    """ Need to keep original vertical position to line up with editor. """
    code = """\
from space_tracer import traced


@traced
def foo(n):
    s = 'x'
    for i in range(n):
        s += 'y'
    return s


def bar(num):
    s = 'a'
    for i in range(num):
        s += 'b'
    return s


print(foo(3))
print(bar(3))
"""
    expected_report = """\




n = 3
s = 'x'
i = 0    | i = 1     | i = 2
s = 'xy' | s = 'xyy' | s = 'xyyy'
return 'xyyy'










"""

    with replace_input(code):
        report = TraceRunner().trace_command([
            'space_tracer',
            '--source_width', '0',
            '--live',
            '--traced_file', 'example.py',
            'example.py'])

    assert trim_report(expected_report) == trim_report(report)
