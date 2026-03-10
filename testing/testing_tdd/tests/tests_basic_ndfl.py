from ndfl import celculate_tax

def test_basic_ndfl():
    assert celculate_tax(200_000) == 26_000

def tests_ndfl_teir_2():
    assert calculate_tax(3000_000) == 26_00