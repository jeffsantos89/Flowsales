import datetime

def format_currency(value):
    return f"R${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_time_period():
    now = datetime.datetime.now()
    return {
        "start_date": now - datetime.timedelta(days=30),
        "end_date": now
    }
    def format_date(date: datetime.datetime) -> str:
        """Format datetime object to Brazilian date format."""
        return date.strftime("%d/%m/%Y")

    def validate_currency(value: float) -> float:
        """Validate and sanitize currency value."""
        if not isinstance(value, (int, float)):
            raise ValueError("Currency value must be numeric")
        return round(float(value), 2)

    def get_time_period_with_validation(days: int = 30) -> dict:
        """Get time period with validation and error handling."""
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days must be a positive integer")
        try:
            now = datetime.datetime.now()
            return {
                "start_date": now - datetime.timedelta(days=days),
                "end_date": now,
                "period_days": days
            }
        except Exception as e:
            raise RuntimeError(f"Error calculating time period: {str(e)}")

    def is_business_hour() -> bool:
        """Check if current time is within business hours (8AM-6PM)."""
        now = datetime.datetime.now()
        return 8 <= now.hour < 18 and now.weekday() < 5