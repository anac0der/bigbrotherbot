import requests
from botmanager import BotManager

token = "af72ff76ba524fbd9812898ef1c33ad5aa8df41da24d8736f2cf3a6f320bb0ba5a8c2690d10ec4ad986b2"
super_user_id = 2222222 #здесь должен быть ваш id
data = requests.get('https://api.vk.com/method/messages.getLongPollServer',
                    params={'access_token': token, 'v':'5.131'}).json()['response']
bot_manager = BotManager(super_user_id, data, token)
bot_manager.main()
#TODO - вынести это в BotManager
'''
while(True):
    if (time_cntr % 300 == 0):
        tm = time.gmtime(time.time())
        print(tm)
        if tm.tm_wday in BotManager.CONTROL_DAYS:
            if time_compare([tm.tm_hour, tm.tm_min], BotManager.CONTROL_TIMES[attempt % a_n]):
                print(1)
                if is_sleep:
                    is_sleep = False
                for bot in users_bot_class_dict.values():
                    if not bot.IS_ANSWERED:
                        requests.get('https://api.vk.com/method/messages.send',
                            params={'access_token': token, 'user_id': bot.USER_ID, 'random_id': randint(-2 ** 32, 2 ** 32), 
                            'message': bot.start_collecting_attendance(), 'v':'5.131', 
                            'keyboard': bot.KEYBOARDS[bot._USER_INPUT]})

                attempt += 1   
            elif not is_sleep and time_compare([tm.tm_hour, tm.tm_min], BotManager.SEND_TIME):
                print(11)
                requests.get('https://api.vk.com/method/messages.send',
                            params={'access_token': token, 'user_id': BotManager.SUPERUSER_ID, 'random_id': randint(-2 ** 32, 2 ** 32), 
                            'message': bot_manager.get_statistics(users_bot_class_dict.values()), 'v':'5.131', 
                            'keyboard': bot.KEYBOARDS[bot._USER_INPUT]})
                for bot in users_bot_class_dict.values():
                    bot.reset_and_sleep()
                is_sleep = True     

        time_cntr = 0

    if(time_cntr % 2 == 0):
        updates = requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=0.5&mode=2&version=2'.format(server = data['server'], 
            key = data['key'], ts = ts)).json()
        ts = updates['ts']
        for update in updates['updates']:
            if update[0] == 4 and not update[2] & 2:
                user_id = update[3]
                if user_id not in users_bot_class_dict and user_id in BotManager._ALLOWED_IDS:
                    users_bot_class_dict[user_id] = Bot(user_id, bot_manager)
                bot = users_bot_class_dict[user_id]
                user_message = update[5]
                bot_answer = bot.update_screen(user_message)
                if bot_answer != None:
                    response = requests.get('https://api.vk.com/method/messages.send',
                        params={'access_token': token, 'user_id': user_id, 'random_id': randint(-2 ** 32, 2 ** 32), 
                        'message': bot_answer, 'v':'5.131', 
                        'keyboard': bot.KEYBOARDS[bot._USER_INPUT]}).json()
                    print(response)
    time_cntr += 1
    sleep(0.2)
'''




    

