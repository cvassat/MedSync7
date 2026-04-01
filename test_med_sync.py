import sys
from unittest.mock import MagicMock
from datetime import datetime, timedelta

# Stub streamlit and supabase before importing the app module so that
# module-level UI/network calls are not executed during test collection.
mock_st = MagicMock()
mock_st.session_state = {}
mock_st.tabs.return_value = [MagicMock(), MagicMock()]
sys.modules['streamlit'] = mock_st
sys.modules['supabase'] = MagicMock()

from med_sync_app_final import calculate_sync_quantities  # noqa: E402


def _future_date(days):
    return (datetime.today() + timedelta(days=days)).strftime("%Y-%m-%d")


def _days_until(date_str):
    """Return days_until_sync the same way calculate_sync_quantities does."""
    return (datetime.strptime(date_str, "%Y-%m-%d") - datetime.today()).days


def test_new_medication_units():
    """New medication units = daily_dose * days_until_sync."""
    daily_dose = 2
    new_med = {'name': 'Metformin', 'daily_dose': daily_dose}
    sync_date = _future_date(10)
    days = _days_until(sync_date)
    result = calculate_sync_quantities([], new_med, sync_date)
    assert len(result) == 1
    entry = result[0]
    assert entry['name'] == 'Metformin (new)'
    assert entry['units_needed'] == daily_dose * days


def test_existing_medication_enough_supply():
    """When an existing med has enough supply, 0 extra units are needed."""
    current_meds = [{'name': 'Lisinopril', 'daily_dose': 1, 'remaining': 30}]
    new_med = {'name': 'NewDrug', 'daily_dose': 1}
    result = calculate_sync_quantities(current_meds, new_med, _future_date(10))
    lisinopril = next(r for r in result if r['name'] == 'Lisinopril')
    assert lisinopril['units_needed'] == 0


def test_existing_medication_insufficient_supply():
    """When an existing med runs short, the correct top-up is returned."""
    remaining = 5
    daily_dose = 1
    current_meds = [{'name': 'Atorvastatin', 'daily_dose': daily_dose, 'remaining': remaining}]
    new_med = {'name': 'NewDrug', 'daily_dose': 1}
    sync_date = _future_date(15)
    days = _days_until(sync_date)
    days_left = remaining // daily_dose
    expected = max((days - days_left) * daily_dose, 0)
    result = calculate_sync_quantities(current_meds, new_med, sync_date)
    atorvastatin = next(r for r in result if r['name'] == 'Atorvastatin')
    assert atorvastatin['units_needed'] == expected


def test_past_sync_date_returns_empty():
    """A sync date in the past should return an empty list."""
    new_med = {'name': 'TestMed', 'daily_dose': 1}
    past_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    result = calculate_sync_quantities([], new_med, past_date)
    assert result == []


def test_multiple_medications():
    """All existing meds plus the new med appear in the result."""
    current_meds = [
        {'name': 'MedA', 'daily_dose': 2, 'remaining': 10},
        {'name': 'MedB', 'daily_dose': 1, 'remaining': 20},
    ]
    new_med = {'name': 'MedC', 'daily_dose': 3}
    result = calculate_sync_quantities(current_meds, new_med, _future_date(20))
    names = [r['name'] for r in result]
    assert 'MedA' in names
    assert 'MedB' in names
    assert 'MedC (new)' in names
