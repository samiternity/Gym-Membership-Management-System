import datetime
import uuid

def get_current_date_iso():
    """Returns the current date in ISO format (YYYY-MM-DD)."""
    return datetime.date.today().isoformat()

def get_current_datetime_iso():
    """Returns the current datetime in ISO format (YYYY-MM-DDTHH:MM:SS)."""
    return datetime.datetime.now().isoformat().split('.')[0]

def generate_unique_id(prefix):
    """Generates a unique ID with a given prefix."""
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"

def calculate_end_date(start_date_iso, duration_months):
    """Calculates the end date based on start date and duration in months."""
    start_date = datetime.date.fromisoformat(start_date_iso)
    duration_days = duration_months * 30  # Convert months to days
    end_date = start_date + datetime.timedelta(days=duration_days)
    return end_date.isoformat()

