import datetime
import vk_api
from vk_api.keyboard import VkKeyboard
from time import sleep, strftime
import requests
from datetime import datetime
import time
from bot import Bot
from random import randint
import json
from keyboard import Keyboard
from socket import error as SocketError

class BotManager(Keyboard):
    def __init__(self, superuser_id, data, token):
        self._ALLOWED_IDS = [superuser_id]

        self.CONTROL_DAYS = [0, 1 ,4]
        self.CONTROL_TIMES = [[13, 0], [14, 30], [16, 0], [17, 30], [19, 0]]
        self.SEND_TIME = [23, 30]
        self.LOG = open("log{}.txt".format(strftime("%d%m%y", time.gmtime(time.time()))), "w")
        self.ATTEMPT_NUMBER = len(self.CONTROL_TIMES)
        self.USERS_BOT_CLASS_DICT = {}   
        self.SUPERUSER_ID = superuser_id
        self._SU_MODE = False
        self.ATTENDANCE_LOG = open('attendance_log.txt', 'a')
        self.SLEEP_TIME = 0.2
        self.TIME_DELAY = 90 / self.SLEEP_TIME #1.5 минуты
        self.IS_SLEEP = True
        self.LP_DATA = data
        self.TS = data['ts']
        self.VERSION = '5.131'
        self.TOKEN = token
        self.FREE_INPUT = False
        self.ERROR_COUNTER = 0
        
        self._SU_INPUT = 'wait_for_su_command'
        self.SU_COMMANDS = {'read_su_command':['/add_id', '/change_dates', '/ids', 
                           '/allowed_ids', '/quit'],
                          'wait_for_su_command':['/su', '/quit'],
                          'wait_for_id':['/quit'],
                          'wait_for_days':['/quit']
                          }

        self.SU_KEYBOARDS = {}
        for inp in self.SU_COMMANDS.keys():
            if(self.SU_COMMANDS[inp]):
                self.SU_KEYBOARDS[inp] = self.create_keyboard(self.SU_COMMANDS[inp], True)
            else:
                self.SU_KEYBOARDS[inp] = self.create_keyboard(["привет!"], True)

    def time_compare(self, time_arr1, time_arr2):
        return time_arr1[0] * 60 + time_arr1[1] >= time_arr2[0] * 60 + time_arr2[1]
    
    def log_write(self, string):       
        try:
            print(string)
            self.LOG.write(string)
        except Exception:
            print('Unable to write it in a log!')
            self.send_error_msg()

    def main(self):
        for uid in self._ALLOWED_IDS:
            self.USERS_BOT_CLASS_DICT[uid] = Bot(uid)
        attempt = 0
        time_cntr = 0
        while(True):
            if (time_cntr % self.TIME_DELAY == 0):
                tm = time.gmtime(time.time())
                if tm.tm_wday in self.CONTROL_DAYS:
                    time_to_send_stat = self.time_compare([tm.tm_hour, tm.tm_min], self.SEND_TIME)
                    if not self.IS_SLEEP and time_to_send_stat:
                        tm = time.gmtime(time.time())
                        self.log_write("Time now: " + strftime("%d-%m-%y %X", tm) + '\n')
                        self.log_write('Sending statistics...\n')
                        self.send_statistics() 
                        attempt = 0
                    elif self.time_compare([tm.tm_hour, tm.tm_min], self.CONTROL_TIMES[attempt % self.ATTEMPT_NUMBER]) and not time_to_send_stat and attempt < self.ATTEMPT_NUMBER:
                        self.log_write('Start collecting statistics...')
                        if self.IS_SLEEP:
                            self.IS_SLEEP = False
                        self.start_collecting()
                        attempt += 1   
                        
                time_cntr = 0
            self.process_updates()
            time_cntr += 1
            sleep(self.SLEEP_TIME)
    
    def process_updates(self):
        try:
            updates = requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=0.5&mode=2&version=2'.format(server = self.LP_DATA['server'], 
                        key = self.LP_DATA['key'], ts = self.TS)).json()
            if 'ts' in updates.keys():
                self.TS = updates['ts']
            else:
                self.LP_DATA = requests.get('https://api.vk.com/method/messages.getLongPollServer',
                    params={'access_token': self.TOKEN, 'v': self.VERSION}).json()['response']
                self.TS = self.LP_DATA['ts']
                updates = requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=0.5&mode=2&version=2'.format(server = self.LP_DATA['server'], 
                        key = self.LP_DATA['key'], ts = self.TS)).json()
            if 'updates' in updates.keys():
                for update in updates['updates']:
                    if update[0] == 4 and not update[2] & 2:
                        user_id = update[3]
                        if user_id not in self.USERS_BOT_CLASS_DICT and user_id in self._ALLOWED_IDS:
                            self.USERS_BOT_CLASS_DICT[user_id] = Bot(user_id)
                            self.log_write('New user: ' + str(user_id) + '\n')
                        bot = self.USERS_BOT_CLASS_DICT[user_id]
                        user_message = update[5]
                        self.log_write("New message from {}:\n".format(str(user_id)))
                        if(user_message and (user_message[0] == '/' or self._SU_MODE) and user_id == self.SUPERUSER_ID):                            
                            bot_answer = self.update_superuser_screen(user_message) 
                            keyboard = self.SU_KEYBOARDS[self._SU_INPUT]
                        else:
                            bot_answer = bot.update_screen(user_message)
                            keyboard = bot.KEYBOARDS[bot._USER_INPUT]
                        if bot_answer != None:
                            response = requests.get('https://api.vk.com/method/messages.send',
                                params={'access_token': self.TOKEN, 'user_id': user_id, 'random_id': randint(-2 ** 32, 2 ** 32), 
                                'message': bot_answer, 'v': self.VERSION, 
                                'keyboard': keyboard}).json()
        except KeyError:
            self.log_write('Error occurs while updating!!!\n')
            self.log_write(updates)
            self.send_error_msg()
        except SocketError:
            try:
                self.LP_DATA = requests.get('https://api.vk.com/method/messages.getLongPollServer',
                        params={'access_token': self.TOKEN, 'v': self.VERSION}).json()['response']
                self.TS = self.LP_DATA['ts']
                self.send_error_msg()
                self.log_write('SocketError! Cannot process updates')
            except Exception:
                self.send_error_msg()
                self.log_write('Double SocketError! Cannot process updates')


    def start_collecting(self):
        for bot in self.USERS_BOT_CLASS_DICT.values():
            if not bot.IS_ANSWERED:
                try:
                    requests.get('https://api.vk.com/method/messages.send',
                        params={'access_token': self.TOKEN, 'user_id': bot.USER_ID, 'random_id': randint(-2 ** 32, 2 ** 32), 
                        'message': bot.start_collecting_attendance(), 'v': self.VERSION, 
                        'keyboard': bot.KEYBOARDS[bot._USER_INPUT]})
                except Exception:
                    self.log_write('Error occurs while collecting stat!\n')
                    self.send_error_msg()

    def send_statistics(self):
        bot = self.USERS_BOT_CLASS_DICT[self.SUPERUSER_ID]
        requests.get('https://api.vk.com/method/messages.send',
            params={'access_token': self.TOKEN, 'user_id': self.SUPERUSER_ID, 'random_id': randint(-2 ** 32, 2 ** 32), 
            'message': self.get_statistics(), 'v': self.VERSION, 
            'keyboard': bot.KEYBOARDS[bot._USER_INPUT]})
        for bot in self.USERS_BOT_CLASS_DICT.values():
            bot.reset_and_sleep()
        self.IS_SLEEP = True
    
    def send_error_msg(self):
        bot = self.USERS_BOT_CLASS_DICT[self.SUPERUSER_ID]
        try:
            requests.get('https://api.vk.com/method/messages.send',
                params={'access_token': self.TOKEN, 'user_id': self.SUPERUSER_ID, 'random_id': randint(-2 ** 32, 2 ** 32), 
                'message': 'Произошла ошибка в работе бота!', 'v': self.VERSION, 
                'keyboard': bot.KEYBOARDS[bot._USER_INPUT]})
        except Exception:
            self.log_write('Error occurs while sending error message!\n')

    def get_statistics(self):
        message = ''
        for bot in self.USERS_BOT_CLASS_DICT.values():
            try:               
                if not bot.IS_ANSWERED:
                    message += bot.USER_NAME
                    message += ': проигнорировал'
                elif not bot.WAS_ON_PAIR:
                    message += bot.USER_NAME
                    if bot.IS_RESPECTFUL:
                        message += ': уважительная причина'
                    else:
                        message += ': ' + bot.COMMENT
                message += '\n'
            except AttributeError:
                continue

        return 'Сегодня отсутствовали:\n' + message

    #super user methods
    def add_allowed_id(self, id):
        self._ALLOWED_IDS.append(id)

    def set_su_input(self, string):
        self._SU_INPUT = string;

    def update_superuser_screen(self, message):
        #if self.IS_SLEEP:
            #return 'Режим суперюзера доступен, только когда бот спит!\n'
        return self.read_su_command(message)
    
    def su_mode_on(self):
        self._SU_MODE = True

    def su_mode_off(self):
        self._SU_MODE = False

    def read_su_command(self, message):
        message = message.lower()
        if message == '/quit':
            self.set_su_input('wait_for_su_command')
            self.su_mode_off()
            return 'Выход из SU - режима'
        if message in self.SU_COMMANDS.get(self._SU_INPUT) or self.FREE_INPUT:
            if self._SU_INPUT == 'wait_for_su_command':
                self.su_mode_on()
                self.set_su_input('read_su_command')
                return 'Что хочешь сделать?'
            if self._SU_INPUT == 'read_su_command':
                if message == '/add_id':
                    self.set_su_input('wait_for_id')
                    self.FREE_INPUT = True
                    return 'Введите id пользователя'

                if message == '/change_dates':
                    self.set_su_input('wait_for_days')
                    self.FREE_INPUT = True
                    return self.form_date_message()

                if message == '/ids':
                    message = 'Активные пользователи:\n'
                    for bot in self.USERS_BOT_CLASS_DICT.values():
                        message += bot.USER_NAME + ' ' + str(bot.USER_ID) + '\n'
                    self.set_su_input('read_su_command')
                    return message

                if message == '/allowed_ids':
                    self.set_su_input('read_su_command')
                    return self.print_allowed_ids()

            if self._SU_INPUT == 'wait_for_id':
                self.set_su_input('read_su_command')
                self.FREE_INPUT = False
                try:
                    response =  requests.get('https://api.vk.com/method/users.get', params={'user_ids': message, 
                    'access_token': self.TOKEN,'v': self.VERSION}).json()['response']   
                    print(response)                
                    if response[0]['first_name'] == 'DELETED':                        
                        return 'Неправильный id пользователя!'
                    self.add_allowed_id(response[0]['id'])
                    return 'id успешно добавлен!'
                except Exception:
                    return 'Ошибка при получении id!'

            if self._SU_INPUT == 'wait_for_days':
                self.FREE_INPUT = False
                if message.isdigit() and int(message) >= 0 and int(message) <= 6:
                    if int(message) not in self.CONTROL_DAYS:
                        self.CONTROL_DAYS.append(int(message))
                    self.set_su_input('read_su_command')
                    return 'Дата успешно добавлена!'
                else:
                    return 'Проверьте ввод!'
        else:
            return 'Ошибка при вводе!'

    def form_date_message(self):
        message = 'Текущие очные дни: '
        for day in self.CONTROL_DAYS:
            message += str(day) + ' '
        message += '\nНапишите цифру от 0(понедельник) до 6(воскресенье)\n'
        return message

    def print_allowed_ids(self):
        message = 'Все разрешенные пользователи:\n'
        if not self.USERS_BOT_CLASS_DICT:
            return 'WTF? В боте 0 активных пользователей!'
        for id in self._ALLOWED_IDS:
            try:
                message += list(self.USERS_BOT_CLASS_DICT.values())[0].parse_user_name(id) + ' '
            except Exception:
                message += '<exception raised>' + ' '
            message += str(id) + '\n'
        return message




    
        


    




    
