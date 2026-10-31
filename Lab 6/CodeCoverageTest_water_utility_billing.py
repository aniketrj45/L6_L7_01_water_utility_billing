
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


def test_invalid_accounts():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10)

    with pytest.raises(ValueError):
        calculate_water_bill([], -1)


def test_empty_and_inactive_accounts():
    result = calculate_water_bill([], 10)
    assert result == {"total_billed": 0.0, "status": "NO_ACTIVITY"}

    accounts = [{"is_active": False, "usage_blocks": [50]}]
    result = calculate_water_bill(accounts, 10)
    assert result["status"] == "NO_ACTIVITY"
    assert result["total_billed"] == 0.0


def test_residential_usage_and_high_usage_break():
    accounts = [{
        "is_active": True,
        "is_commercial": False,
        "usage_blocks": [20, 60, 120, 10]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 730.0
    assert result["status"] == "NORMAL"


def test_commercial_usage_and_leak_waiver():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "has_leak_waiver": True,
        "usage_blocks": [0, -5, 20, 60, 120]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 560.0
    assert result["status"] == "NORMAL"


def test_leak_waiver_without_deduction():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [10]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 25.0


def test_excessive_flags():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [0, 0, 0, 0, 0, 0]
    }]
    result = calculate_water_bill(accounts, 10)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_meter_tampering_no_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_meter_tampering_detected():
    assert check_meter_tampering([[1, -1, -2]]) == "TAMPER_SUSPECTED"


def test_meter_tampering_clear():
    assert check_meter_tampering([[1, -1, 2, -3, 4]]) == "CLEAR"
