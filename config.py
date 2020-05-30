import os
from pytz import timezone

TOKEN = os.environ['BOT_TOKEN']
PORT = int(os.environ.get('PORT', '8443'))
APP_URL = os.environ['APP_URL']
DATABASE_URL = os.environ['DATABASE_URL']
API_KEY_LEN = int(os.environ['API_KEY_LEN'])
SALT_LEN = int(os.environ['SALT_LEN'])
HASH_ALGO = os.environ['HASH_ALGO']
HASH_ITER = int(os.environ['HASH_ITER'])

# Default Timezone
DEFAULT_TZ = timezone('Asia/Singapore')
