from vk_api.keyboard import VkKeyboard
class Keyboard():
    def create_keyboard(self, commands, one_time=True):
        keyboard = VkKeyboard(one_time=one_time)
        button_cnt = 0
        for command in commands:
            if(button_cnt % 3 == 0 and button_cnt > 0):
                keyboard.add_line()               
            keyboard.add_button(command, 'primary')
            button_cnt += 1
        keyboard =  keyboard.get_keyboard()
        return keyboard
