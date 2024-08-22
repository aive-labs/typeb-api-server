import slack_sdk

from src.common.utils.get_env_variable import get_env_variable


def send_slack_message(title, body, member_id=None):
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    token = get_env_variable("slack_token")
    client = slack_sdk.WebClient(token=token)

    message = f"*{title}* \n {body}"
    slack_msg = f"<@{member_id}>\\n {message}" if member_id else f"{message}"

    response = client.chat_postMessage(channel="타입비_알람", text=slack_msg)
