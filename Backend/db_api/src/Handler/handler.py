from Manager.manager import handle_action


def handle(event):
    action = event["action"]
    return handle_action(action, event)
