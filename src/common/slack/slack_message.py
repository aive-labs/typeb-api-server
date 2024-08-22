import slack_sdk

from src.common.utils.get_env_variable import get_env_variable


def send_slack_message(title, body, member_id):
    token = get_env_variable("slack_token")
    client = slack_sdk.WebClient(token=token)

    message = f"*{title}* \n {body}"
    slack_msg = f"<@{member_id}> {title} \n {message}"

    response = client.chat_postMessage(channel="타입비_알람", text=slack_msg)
