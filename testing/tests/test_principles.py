import sys
sys.path.append("../src")

from math_demo import add_with_bug

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

if __name__ = "__main__":
    test_addition()
    test_addition_basic()
    test_bug_addition_notsuffition()
    test_bug_addition_enough()
    test_addition_duplicated_logi()