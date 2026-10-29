
import requests

from config import API_URL


def send_alert(alert):
    """Send one stale-file alert to the existing API."""

    if not API_URL:
        print("API_URL is not configured. Alert was not sent.")
        return False

    try:
        response = requests.post(
            API_URL,
            json=alert,
            timeout=10,
        )

        if 200 <= response.status_code < 300:
            print(
                f"Alert sent successfully: "
                f"{alert.get('file_name', 'Unknown file')}"
            )
            return True

        print(
            f"API rejected the alert. "
            f"Status: {response.status_code}"
        )
        print(f"Response: {response.text}")
        return False

    except requests.RequestException as error:
        print(f"Could not send alert to API: {error}")
        return False


def send_alerts(alerts):
    """Send all generated alerts to the existing API."""

    if not alerts:
        print("No alerts to send.")
        return 0

    successful_sends = 0

    for alert in alerts:
        if send_alert(alert):
            successful_sends += 1

    print(
        f"Alerts sent successfully: "
        f"{successful_sends}/{len(alerts)}"
    )

    return successful_sends


if __name__ == "__main__":
    print("API Client is ready.")

    if API_URL:
        print(f"Configured API endpoint: {API_URL}")
    else:
        print("API_URL is not configured yet.")
