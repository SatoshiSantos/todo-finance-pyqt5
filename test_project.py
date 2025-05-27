from project import format_currency, calculate_credit_usage, validate_float

def test_format_currency():
    assert format_currency(0) == "$0.00"
    assert format_currency(1234.567) == "$1,234.57"
    assert format_currency(1000000) == "$1,000,000.00"

def test_calculate_credit_usage():
    assert calculate_credit_usage(500, 1000) == 50.0
    assert calculate_credit_usage(0, 1000) == 0.0
    assert calculate_credit_usage(500, 0) == 0.0

def test_validate_float():
    assert validate_float("100") == 100.0
    assert validate_float("12.5") == 12.5
    assert validate_float("abc") is None
    assert validate_float(None) is None
