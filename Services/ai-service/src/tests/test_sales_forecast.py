import pytest
from unittest.mock import patch
from src.sales_forecast import SalesForecast

@pytest.fixture
def sales_forecast():
    return SalesForecast()

def test_initial_forecast(sales_forecast):
    assert sales_forecast.forecast == []

@patch('src.sales_forecast.SalesForecast._load_data')
def test_load_data(mock_load_data, sales_forecast):
    mock_load_data.return_value = [{'date': '2023-01-01', 'sales': 100}]
    sales_forecast.load_data()
    assert sales_forecast.data == [{'date': '2023-01-01', 'sales': 100}]

@pytest.mark.parametrize("input_data, expected", [
    ([{'date': '2023-01-01', 'sales': 100}], [{'date': '2023-01-02', 'sales': 110}]),
    ([{'date': '2023-01-01', 'sales': 200}], [{'date': '2023-01-02', 'sales': 220}]),
])
def test_forecast_generation(input_data, expected, sales_forecast):
    with patch('src.sales_forecast.SalesForecast._load_data', return_value=input_data):
        sales_forecast.load_data()
        sales_forecast.generate_forecast()
        assert sales_forecast.forecast == expected

def test_forecast_accuracy(sales_forecast):
    sales_forecast.data = [{'date': '2023-01-01', 'sales': 100}, {'date': '2023-01-02', 'sales': 110}]
    sales_forecast.generate_forecast()
    accuracy = sales_forecast.calculate_accuracy()
    assert 0 <= accuracy <= 1

if __name__ == "__main__":
    pytest.main()