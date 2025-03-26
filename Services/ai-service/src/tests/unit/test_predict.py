import pytest
from services.predict_service import predict_sales

def test_predict_sales():
    data = {"historical_sales": [100, 200, 300], "trend_factor": 1.2}
    prediction = predict_sales(data)
    assert prediction > 0
    def test_predict_sales_with_empty_data():
        with pytest.raises(ValueError):
            predict_sales({})

    def test_predict_sales_with_invalid_trend():
        data = {"historical_sales": [100, 200, 300], "trend_factor": -1}
        with pytest.raises(ValueError):
            predict_sales(data)

    def test_predict_sales_with_zero_sales():
        data = {"historical_sales": [0, 0, 0], "trend_factor": 1.0}
        prediction = predict_sales(data)
        assert prediction == 0

    def test_predict_sales_trend_calculation():
        data = {"historical_sales": [100, 200, 300], "trend_factor": 2.0}
        prediction = predict_sales(data)
        assert prediction > max(data["historical_sales"])

    @pytest.mark.parametrize("sales,trend", [
        ([100, 200, 300], 1.5),
        ([50, 75, 100], 1.2),
        ([1000, 900, 800], 0.8)
    ])
    def test_predict_sales_multiple_scenarios(sales, trend):
        data = {"historical_sales": sales, "trend_factor": trend}
        prediction = predict_sales(data)
        assert isinstance(prediction, (int, float))
        assert prediction >= 0