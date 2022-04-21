import requests
from keyboard import Keyboard
import random
class Bot(Keyboard):
    WELCOME_MSG = 'Привет - привет!'
    COMMANDS = {'read_answer':['да', 'нет', 'частично'], 
                'is_respectful':['да', 'нет', 'комментарий'],
                'sleeping':[],
                'recollect_stat':['да', 'нет'],
                'waiting':[],
                'comment':[]}
    KEK = ['нет']
    QUESTION_TEXT = 'Привет! Большой Брат очень хочет знать, был(a) ли ты сегодня на парах!'
    WRONG_COMMAND_TEXT = 'Проверь ввод! Разрешенные команды: '
    THANK_TEXT = 'Информация принята. Спасибо!'
    TOKEN = "af72ff76ba524fbd9812898ef1c33ad5aa8df41da24d8736f2cf3a6f320bb0ba5a8c2690d10ec4ad986b2"
    VERSION = '5.131'
    KEYBOARDS = {}
                  
    def __init__(self, user_id):
        self.USER_ID = user_id
        self._USER_INPUT = 'sleeping'
        self.WAS_ON_PAIR = False
        self.IS_RESPECTFUL = False
        self.IS_ANSWERED = False
        self.COMMENT = ''
        self.USER_NAME = self.parse_user_name(user_id)
        for inp in Bot.COMMANDS.keys():
            if(Bot.COMMANDS[inp]):
                Bot.KEYBOARDS[inp] = self.create_keyboard(Bot.COMMANDS[inp], True)
            else:
                Bot.KEYBOARDS[inp] = self.create_keyboard(["привет!"], True)          

    def parse_user_name(self, user_id):
        try:
            data = requests.get('https://api.vk.com/method/users.get', params={'user_ids': user_id, 'access_token': Bot.TOKEN, 
                'v': Bot.VERSION}).json()['response']
            user_name = data[0]['last_name'] + ' ' + data[0]['first_name']
            return user_name
        except Exception:
            print('Cannot parse user name, user_id: ' + str(self.USER_ID))
            return '<{}>'.format(str(self.USER_ID))

    def user_input_set(self, string):
        self._USER_INPUT = string

    def update_screen(self, message):
        #if message[0] == '/' and self.USER_ID == Bot.BOT_MANAGER.SUPERUSER_ID:
           # return BOT_MANAGER.update_super_user_screen(message)

        if self._USER_INPUT == 'sleeping':
            return 'Я сплю. Тебя надо сдать Полиции Мыслей!'
        if self._USER_INPUT == 'waiting':
            self.user_input_set('recollect_stat')
            return 'Ты хочешь уведомить меня о своей посещаемости?'
        if self._USER_INPUT == 'comment':
                self.COMMENT = message
                self.user_input_set('sleeping')
                self.IS_ANSWERED = True
                return Bot.THANK_TEXT
        return self.read_command(message)

    def read_command(self, message):
        message = message.lower()
        if message in Bot.COMMANDS.get(self._USER_INPUT):
            if self._USER_INPUT == 'read_answer':
                if message == 'да':
                    self.WAS_ON_PAIR = True
                    self.user_input_set('waiting')
                    self.IS_ANSWERED = True
                    if random.randint(0, 100) == 42:
                        return random.choice(Bot.KEK)
                    return Bot.THANK_TEXT
                else:
                    self.user_input_set('is_respectful')
                    return 'Ты пропустил пары по уважительной причине?'  
            if self._USER_INPUT == 'is_respectful':
                if message == 'да':
                    self.IS_RESPECTFUL = True
                    if random.randint(0, 100) == 42:
                        self.user_input_set('waiting')
                        self.IS_ANSWERED = True
                        return random.choice(Bot.KEK)
                if message == 'нет':
                    self.IS_RESPECTFUL = False
                if message == 'комментарий':
                    self.user_input_set('comment')
                    return None
                self.user_input_set('waiting')
                self.IS_ANSWERED = True
                return Bot.THANK_TEXT
            if self._USER_INPUT == 'recollect_stat':
                if message == 'да':
                    return self.start_collecting_attendance()
                self.user_input_set('waiting')
                return 'Тогда я дальше спать!'
        else:
            return Bot.WRONG_COMMAND_TEXT + self.right_commands()

    def start_collecting_attendance(self):
        self.IS_ANSWERED = False
        self.WAS_ON_PAIR = False
        self.IS_RESPECTFUL = False
        self.user_input_set('read_answer')
        return Bot.QUESTION_TEXT

    def right_commands(self):
        right_commands = ''
        for command in Bot.COMMANDS.get(self._USER_INPUT):
            right_commands += command
            right_commands += ' '
        return right_commands

    def reset_and_sleep(self):
        self.user_input_set('sleeping')
        self.WAS_ON_PAIR = False
        self.IS_RESPECTFUL = False
        self.IS_ANSWERED = False
        self.COMMENT = ''





                    



 

