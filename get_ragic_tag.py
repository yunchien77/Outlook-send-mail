import requests
from dotenv import load_dotenv
import os
####################
target_tag = '合作夥伴'
####################
load_dotenv()
API_KEY = os.getenv('RAGIC_API_KEY')

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '4'

ROW_INDEX = '1'

params = {
    'api': '',
    'v': 3,
    'filter': f'1={ROW_INDEX}'
}

API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})
print(response.text)

data = response.json()  # 將 JSON 資料轉換成 Python 字典

for key, value in data.items():
    name = value.get('姓名', '')
    email = value.get('電子郵件1', '')
    tags = ', '.join(value.get('標籤', []))
    
    if target_tag in tags:
        print(f'姓名: {name}, 電子郵件: {email}, 標籤: {tags}')