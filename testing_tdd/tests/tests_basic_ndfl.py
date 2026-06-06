from ndfl import calculate_tax

def test_basic_ndfl():
    assert calculate_tax(200_000) == 26_000

def test_ndfl_tier_2():
    # 312_000 + (3_000_000 - 2_400_000) * 0.15 = 312_000 + 90_000 = 402_000
    assert calculate_tax(3_000_000) == 402_000 

def test_ndfl_tier_3():
    # 702_000 + (7_000_000 - 5_000_000) * 0.18 = 702_000 + 360_000 = 1_062_000
    assert calculate_tax(7_000_000) == 1_062_000

def test_ndfl_tier_4():
    # 3_402_000 + (30_000_000 - 20_000_000) * 0.20 = 3_402_000 + 2_000_000 = 5_402_000
    assert calculate_tax(30_000_000) == 5_402_000

def test_ndfl_tier_5():
    # 9_402_000 + (70_000_000 - 50_000_000) * 0.22 = 9_402_000 + 4_400_000 = 13_802_000
    assert calculate_tax(70_000_000) == 13_802_000