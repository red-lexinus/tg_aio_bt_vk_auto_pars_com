from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup


class KeyboardGenerator:
    def __init__(self, main_row=1):
        self.main_row = main_row
        self.main_action_cb = CallbackData("main_action", "action")
        self.dell_massage_cb = CallbackData("dell", "answer")
        self.multiple_choice_cb = CallbackData('choice', 'filter', 'res')
        self.quick_answer_cb = CallbackData('reply', 'message')

    def return_callback_data(self) -> list[CallbackData]:
        return [self.main_action_cb, self.dell_massage_cb, self.multiple_choice_cb, self.quick_answer_cb]

    def create_start_command_ikb(self, buttons_data: list[str]) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=self.main_row)
        for i in buttons_data:
            kb.add(i)
        return kb

    def create_main_action_ikb(self, buttons_data: list[list[str, str]]) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(button_data[0], callback_data=self.main_action_cb.new(button_data[1]))] for
            button_data
            in buttons_data
        ])
        return ikb

    def create_dell_message_ikb(self, buttons_data: list[list[str, str]],
                                button_message: str = 'Удалить ответ') -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(button_message, callback_data=self.dell_massage_cb.new(button_data[0]))] for
            button_data in buttons_data
        ])
        return ikb

    def create_quick_answer_ikb(self, quick_answer: list[list[str, str]], group_id: int,
                                post_id: int) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(answer[1],
                                  callback_data=self.quick_answer_cb.new(f'{group_id}_{post_id}_{answer[0]}'))] for
            answer in quick_answer
        ])
        return ikb

    def create_multiple_choice_ikb(self, large_buttons_data: list[list[str, str, str]]):
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(button_data[0], callback_data=self.multiple_choice_cb.new(
                button_data[1], button_data[2]))] for button_data in large_buttons_data
        ])
        return ikb

    def create_main_action_or_link_ikb(self, buttons_link_data: list[list[str, str, bool]]):
        ikb = InlineKeyboardMarkup()
        for button_link_data in buttons_link_data:
            if button_link_data[2]:
                ikb.add(InlineKeyboardButton(button_link_data[0], callback_data=self.main_action_cb.new(
                    button_link_data[1])))
            else:
                ikb.add(InlineKeyboardButton(button_link_data[0], url=button_link_data[1]))
        return ikb
