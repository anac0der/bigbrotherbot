from keyboard import Keyboard
import requests 
class Superuser(Keyboard, BotManager):
    def __init__(self, token, version):
        
        self.TOKEN = token
        self.VERSION = version
    def set_su_input(self, string):
        self._SU_INPUT = string;

    def update_superuser_screen(self, message):
        if self._SU_INPUT == 'wait_for_su_command' and message == '/su':
            self.set_su_input('read_su_command')
            return 'Что хочешь сделать?'
        if self._SU_INPUT == 'read_su_command':
            return read_su_command(message)

    def read_su_command(self, message):
        message = message.lower()
        if message in self.SU_COMMANDS.get(self._SU_INPUT):
            if self._SU_INPUT == 'read_su_command':
                if message == '/add_id':
                    self.set_su_input('wait_for_id')
                    return 'Введите id пользователя'
            if self._SU_INPUT == 'wait_for_id':
                try:
                    response =  requests.get('https://api.vk.com/method/users.get', params={'user_ids': message, 
                    'access_token': self.TOKEN,'v': self.VERSION}).json()['response']
                    if response['first_name'] == 'DELETED':
                        self.set_su_input('read_su_command')
                        return 'Неправильный id пользователя!'
                    
                except Exception:
                    self.set_su_input('read_su_command')
                    return 'Ошибка при получении id!'




    
        


