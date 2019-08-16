import os
from pytz import timezone

TOKEN = os.environ['BOT_TOKEN']
PORT = int(os.environ.get('PORT', '8443'))
APP_URL = os.environ['APP_URL']
DATABASE_URL = os.environ['DATABASE_URL']

# Default Timezone
DEFAULT_TZ = timezone('Asia/Singapore')
