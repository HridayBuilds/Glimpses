from html import escape


def render_email(kind, recipient_name, event_name, event_url, details):
    name = recipient_name or "there"
    title = event_name or "your event"
    messages = {
        "join_request": (
            f"New request to join {title}",
            f"{details.get('requesterName') or 'Someone'} requested to join {title}.",
            "Review request",
        ),
        "approved": (f"You can join {title}", f"Your request to join {title} was approved.", "View event"),
        "declined": (f"Your request for {title}", f"Your request to join {title} was declined.", None),
        "photos_ready": (
            f"Your photos from {title} are ready",
            f"You have {details.get('photoCount', 0)} photos of you in {title}.",
            "View your photos",
        ),
        "upload_success": (
            f"Your upload to {title} is complete",
            f"Your upload to {title} is complete. {details.get('succeededCount', 0)} photos were added.",
            "View event",
        ),
        "upload_failed": (
            f"Your upload to {title} failed",
            f"Your upload to {title} could not be completed. Please try again.",
            "Try again",
        ),
        "archived": (
            f"{title} has been archived",
            f"{title} is now archived. You can still view and download its photos, but no new photos can be uploaded.",
            "View event",
        ),
        "deleted": (
            f"{title} has been deleted",
            f"{title} and its photos have been deleted from Glimpses.",
            None,
        ),
    }
    subject, message, button = messages[kind]
    greeting = f"Hi {name},"
    text = f"{greeting}\n\n{message}"
    if button:
        text += f"\n\n{button}: {event_url}"
    text += "\n\nYou can change email notifications in your Glimpses profile."

    button_html = ""
    if button:
        button_html = (
            f'<a href="{escape(event_url, quote=True)}" style="display:inline-block;'
            'background:#FF7A59;color:#200C05;text-decoration:none;font-weight:700;'
            'padding:12px 18px;border-radius:8px">'
            f"{escape(button)}</a>"
        )
    html = (
        '<!doctype html><html><body style="margin:0;padding:24px;background:#f5f5f7;'
        'font-family:Arial,sans-serif;color:#25252b">'
        '<div style="max-width:560px;margin:auto;padding:28px;background:#ffffff;'
        'border:1px solid #e6e6e9;border-radius:12px">'
        '<p style="font-size:19px;font-weight:700;margin:0 0 24px">Glimpses</p>'
        f'<h1 style="font-size:22px;line-height:1.3;margin:0 0 18px">{escape(subject)}</h1>'
        f'<p style="font-size:15px;line-height:1.6">{escape(greeting)}</p>'
        f'<p style="font-size:15px;line-height:1.6">{escape(message)}</p>'
        f'<p style="margin:26px 0">{button_html}</p>'
        '<p style="font-size:12px;line-height:1.5;color:#666">'
        'You can change email notifications in your Glimpses profile.</p>'
        '</div></body></html>'
    )
    return subject, html, text
