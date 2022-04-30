import requests
from botmanager import BotManager

token = ""
super_user_id = 2222222 #здесь должен быть ваш id
data = requests.get('https://api.vk.com/method/messages.getLongPollServer',
                    params={'access_token': token, 'v':'5.131'}).json()['response']
bot_manager = BotManager(super_user_id, data, token)
bot_manager.main()
#TODO - вынести это в BotManager
