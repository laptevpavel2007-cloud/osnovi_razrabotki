from ndfl import calculate_tax

def test_basic_ndfl():
    assert calculate_tax(200_000) == 26_000

def tests_ndfl_tier_2():
    # Исправлено ожидаемое значение: 312_000 + (3M - 2.4M)*0.15 = 402_000
    assert calculate_tax(3_000_000) == 402_000 

def tests_ndfl_tier_3():
    assert calculate_tax(7_000_000) == 1_062_000

def tests_ndfl_tier_4():
    assert calculate_tax(30_000_000) == 5_402_000

def tests_ndfl_tier_5():
    assert calculate_tax(70_000_000) == 13_802_000