
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


def test_invalid_account_inputs():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10)
    with pytest.raises(ValueError):
        calculate_water_bill([], -1)


def test_empty_and_inactive_accounts():
    assert calculate_water_bill([], 10) == {
        "total_billed": 0.0,
        "status": "NO_ACTIVITY"
    }
    assert calculate_water_bill(
        [{"is_active": False, "usage_blocks": [10]}], 10
    ) == {"total_billed": 0.0, "status": "NO_ACTIVITY"}


def test_all_usage_branches():
    residential = {
        "is_active": True,
        "is_commercial": False,
        "usage_blocks": [0, -2, 20, 60, 120, 10]
    }
    commercial = {
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [20, 60, 120]
    }
    result = calculate_water_bill([residential, commercial], 10)
    assert result["total_billed"] == 1340.0
    assert result["status"] == "NORMAL"


def test_leak_waiver_branches():
    accounts = [
        {"is_active": True, "has_leak_waiver": True,
         "usage_blocks": [100]},
        {"is_active": True, "has_leak_waiver": True,
         "usage_blocks": [120]}
    ]
    result = calculate_water_bill(accounts, 10)
    assert result["total_billed"] == 710.0


def test_excessive_flags_status():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [0, 0, 0, 0, 0, 0]
    }]
    assert calculate_water_bill(accounts, 10)["status"] == "EXCESSIVE_FLAGS"


def test_meter_tampering_branches():
    assert check_meter_tampering([]) == "NO_DATA"
    assert check_meter_tampering([[1, 2, 3]]) == "CLEAR"
    assert check_meter_tampering([[1, -1, 2, -3]]) == "CLEAR"
    assert check_meter_tampering([[1, -1, -2]]) == "TAMPER_SUSPECTED"
