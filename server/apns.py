# coding: utf-8

import asyncio
import os
from datetime import datetime
from pathlib import Path
from time import time

import httpx
import jwt


# https://developer.apple.com/documentation/usernotifications/establishing-a-token-based-connection-to-apns
def __get_jwt_token():
    PRIVATE_KEY_PATH = os.environ.get('APNS_AUTH_KEY_FILE_PATH')
    APNS_KEY_ID = os.environ.get('APNS_AUTH_KEY_ID')
    TEAM_ID = os.environ.get('TEAM_ID')

    private_key = Path(PRIVATE_KEY_PATH).read_text()
    headers = {
        'alg': 'ES256',
        'kid': APNS_KEY_ID
    }
    payload = {
        'iss': TEAM_ID,
        'iat': time()
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers=headers
    )

# https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns


async def send_user_notification():
    print('Sending user notification...')

    BUNDLE_ID = os.environ.get('BUNDLE_ID')
    DEVICE_TOKEN = os.environ.get('DEVICE_TOKEN')
    USE_SANDBOX = os.environ.get('USE_SANDBOX')
    if USE_SANDBOX == '1':
        HOST = 'api.sandbox.push.apple.com'
    else:
        HOST = 'api.push.apple.com'

    token = __get_jwt_token()

    device_tokens = [
        DEVICE_TOKEN
    ]

    headers = {
        'authorization': f'bearer {token}',
        'apns-push-type': 'alert',
        'apns-topic': f'{BUNDLE_ID}'
    }

    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    payload = {
        'aps': {
            'alert': {
                'title': 'Test Title (via APNs with Python)',
                'sound': 'default',
                'body': f'This user notification was sent by requesting APNs directly at {current_datetime}'
            }
        }
    }

    async with httpx.AsyncClient(http2=True) as client:
        for index, device_token in enumerate(device_tokens):
            url = f'https://{HOST}/3/device/{device_token}'

            response = await client.post(
                url,
                headers=headers,
                json=payload
            )

            padded_index = str(index).rjust(2, '0')
            print(f'#{padded_index} device token = {device_token}')
            print(
                f'#{padded_index} response status code: '
                f'{response.status_code}'
            )


# https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns
async def send_voip_push_notification():
    print('Sending VoIP notification...')

    BUNDLE_ID = os.environ.get('BUNDLE_ID')
    DEVICE_TOKEN = os.environ.get('VOIP_DEVICE_TOKEN')
    USE_SANDBOX = os.environ.get('USE_SANDBOX')
    if USE_SANDBOX == '1':
        HOST = 'api.sandbox.push.apple.com'
    else:
        HOST = 'api.push.apple.com'

    token = __get_jwt_token()

    device_tokens = [
        DEVICE_TOKEN
    ]

    headers = {
        'authorization': f'bearer {token}',
        'apns-push-type': 'voip',
        'apns-topic': f'{BUNDLE_ID}.voip'
    }

    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    payload = {
        'aps': {
            'title': 'Test Title (via APNs with Python)',
            'body': f'This VoIP notification was sent at {current_datetime}'
        }
    }

    async with httpx.AsyncClient(http2=True) as client:
        for index, device_token in enumerate(device_tokens):
            url = f'https://{HOST}/3/device/{device_token}'

            response = await client.post(
                url,
                headers=headers,
                json=payload
            )

            padded_index = str(index).rjust(2, '0')
            print(f'#{padded_index} device token = {device_token}')
            print(
                f'#{padded_index} response status code: '
                f'{response.status_code}'
            )


if __name__ == '__main__':
    VOIP_PUSH = os.environ.get('VOIP_PUSH')

    asyncio.run(
        send_voip_push_notification() if VOIP_PUSH == 'true' else send_user_notification()
    )
