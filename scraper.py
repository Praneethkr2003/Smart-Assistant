import requests

def get_attendance(user_id: str, password: str) -> str:
    """Fetch attendance using the provided API endpoint and return as a string."""
    url = (
        "https://a0qna69x15.execute-api.ap-southeast-2.amazonaws.com/dev/attendance?"
        f"student_id={user_id}&password={password}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        # Try to parse JSON for pretty formatting
        try:
            data = resp.json()
            if isinstance(data, dict):
                # Pretty print dict as key: value
                return "\n".join(f"{k}: {v}" for k, v in data.items())
            elif isinstance(data, list):
                return "\n".join(str(item) for item in data)
            else:
                return str(data)
        except Exception:
            return resp.text
    except Exception as e:
        return f"❌ Error fetching attendance: {e}"