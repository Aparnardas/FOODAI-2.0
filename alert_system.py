# utils/alert_system.py

try:
    from plyer import notification
except ImportError:
    notification = None


def send_alert(title, message):

    try:

        if notification:

            notification.notify(
                title=title,
                message=message,
                timeout=5
            )

        else:

            print(f"[ALERT] {title}: {message}")

    except Exception as e:

        print("Notification error:", e)
        print(f"[ALERT] {title}: {message}")
