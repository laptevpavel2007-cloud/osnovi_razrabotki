import sys
sys.path.append("../src")

from math_demo import add_with_bug, add_something

def test_addition():
    assert add_with_bug(2, 2) == 4


def test_addition_basic():
    assert add_with_bug(2, 2) == 4, "function"
    print("tests Basic")

def test_bug_addition_notsuffition():
    assert add_with_bug(2, 2) == 4, "function"
    print("tests bug Basic")

def test_bug_addition_enough():
    assert add_with_bug(2, 2) == 4, "function"
    assert add_with_bug(0, 0) == 0
    assert add_with_bug(5, 6) == 11
    print("tests bug Basic")

def test_addition_duplicated_logi():
    assert add_with_bug(6, 3) == 6+3
    assert add_with_bug(6, 3) == 9
    print("Test Dupl")

def test_addition_overcomplicated():
    for i in range(0, 2**32):
        for j in range(0, 2**32):
            assert add_with_bug(i, j) == i+j
            assert add_with_bug(-i, j) == -i+j
            assert add_with_bug(i, -j) == i-j
            assert add_with_bug(-i, -j) == -i-j

def test_addition_resonable():
    assert add_with_bug(6, 3) == 9
    assert add_with_bug(3, 3) == 3
    assert add_with_bug(0, -3) == -3
    assert add_with_bug(-7, 83) == 76
    assert add_with_bug(-7, -83) == -90

def test_add_something_resonbc10able():
     add_something(6, 3) == 9
     add_something(None, None) == 0
     add_something(None, "abc") == 0
     add_something(None, 10) == 0
     add_something("abc", 10) == "abc10"
     add_something(10, "abc") == "10abc"
     add_something("abc", "xyz") == "abcxyz"


if __name__ = "__main__":
    test_addition()
    test_addition_basic()
    test_bug_addition_notsuffition()
    test_bug_addition_enough()
    test_addition_duplicated_logi()