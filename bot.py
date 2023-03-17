from aiogram import executor, Bot, Dispatcher, types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MediaGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BotBlocked
import asyncio

from aiogram.types import MediaGroup, InputFile, Message

import config
from config import Telegram_Token, Bot_responses, Telegram_bot_id, vk_standard_token
from BotServer import BotServer
from DataBaseServer import DataBaseServer
from KeyboardGenerator import KeyboardGenerator
from VkParser import VkParser

bot = Bot(Telegram_Token)
dp = Dispatcher(bot)
database_server = DataBaseServer()
keyboard_generator = KeyboardGenerator()
bot_server = BotServer(bot, database_server, VkParser(vk_standard_token), keyboard_generator, Bot_responses)

main_action_cb, dell_massage_cb, multiple_choice_cb, quick_answer_cb = keyboard_generator.return_callback_data()


async def on_startup(_) -> None:
    pass


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message) -> None:
    await bot.send_message(msg.from_user.id,
                           f'{msg.from_user.username}' + Bot_responses['start_massage'],
                           reply_markup=keyboard_generator.create_start_command_ikb(
                               [Bot_responses['btn_1'], Bot_responses['btn_2']]))


@dp.callback_query_handler(main_action_cb.filter(action='help'))
async def callback_help(callback: types.CallbackQuery) -> None:
    await callback.answer(Bot_responses['manual_massage_1'], show_alert=True)


@dp.callback_query_handler(main_action_cb.filter(action='add_answer'))
async def callback_add_answer(callback: types.CallbackQuery) -> None:
    await bot.send_message(callback.from_user.id, Bot_responses['add_answer_massage_1'])


@dp.callback_query_handler(main_action_cb.filter(action='rename_token'))
async def callback_dell_token(callback: types.CallbackQuery) -> None:
    tokens = database_server.get_full_tokens_by_user_id(callback.from_user.id)
    large_buttons_data = [[token_data[3], 'rename_token', token_data[0]] for token_data in tokens]
    await bot.send_message(callback.from_user.id, Bot_responses['rename_token_message'],
                           reply_markup=keyboard_generator.create_multiple_choice_ikb(large_buttons_data))


@dp.callback_query_handler(main_action_cb.filter(action='add_token'))
async def callback_add_token(callback: types.CallbackQuery) -> None:
    await callback.message.answer(Bot_responses['add_token_message'])


@dp.callback_query_handler(main_action_cb.filter(action='sett_token'))
async def callback_sett_token(callback: types.CallbackQuery) -> None:
    buttons_link_data = [
        [Bot_responses['get_token_manual_button'], 'manual_get_token', True],
        [Bot_responses['get_token_url_button'], Bot_responses['get_token_url'], False],
        [Bot_responses['add_token_button'], 'add_token', True],
        [Bot_responses['rename_token_button'], 'rename_token', True]
    ]
    keyboard_generator.create_main_action_or_link_ikb(buttons_link_data)
    await bot.send_message(callback.from_user.id, Bot_responses['need_token_1'],
                           reply_markup=keyboard_generator.create_main_action_or_link_ikb(buttons_link_data))


@dp.callback_query_handler(main_action_cb.filter(action='sett_public'))
async def callback_sett_public(callback: types.CallbackQuery) -> None:
    if not database_server.check_user_have_token(callback.from_user.id):
        buttons_data = [
            [Bot_responses['get_token_manual_button'], 'manual_get_token', True],
            [Bot_responses['get_token_url_button'], Bot_responses['get_token_url'], False],
            [Bot_responses['add_token_button'], 'add_token', True],
        ]
        await bot.send_message(callback.from_user.id, Bot_responses['need_token_1'],
                               reply_markup=keyboard_generator.create_main_action_or_link_ikb(buttons_data))
    else:
        public = database_server.get_public_by_user_id(callback.from_user.id)
        if not public:
            await bot.send_message(callback.from_user.id, Bot_responses['setting_public_message_2'])
        else:
            large_buttons_data = [
                [group[1], 'view_group', group[0]] for group in public
            ]
            await bot.send_message(callback.from_user.id, Bot_responses['setting_public_message_1'],
                                   reply_markup=keyboard_generator.create_multiple_choice_ikb(large_buttons_data))


@dp.callback_query_handler(main_action_cb.filter(action='dell_answer'))
async def callback_dell_answer(callback: types.CallbackQuery) -> None:
    answers = database_server.get_full_messages_by_user_id(callback.from_user.id)
    for i in range(len(answers)):
        await bot.send_message(callback.from_user.id, answers[i][1],
                               reply_markup=keyboard_generator.create_dell_message_ikb([answers[i]]))


@dp.callback_query_handler(dell_massage_cb.filter())
async def callback_add_answer(callback: types.CallbackQuery) -> None:
    answer_data = [int(i) for i in callback.data.split(':')[1].split('_')][0]
    database_server.dell_message_by_id(answer_data)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@dp.callback_query_handler(multiple_choice_cb.filter(filter='view_group'))
async def callback_view_id_group(callback: types.CallbackQuery) -> None:
    group_id = int(callback.data.split(':')[-1])
    group_name = database_server.get_public_name_by_id(group_id)
    large_buttons_data = [
        [Bot_responses['unsubscribe_button'], 'unsubscribe', f'{group_id}'],
        [Bot_responses['get_1_post_button'], 'get_posts', f'1_{group_id}'],
        [Bot_responses['get_5_post_button'], 'get_posts', f'5_{group_id}']
    ]
    ikb = keyboard_generator.create_multiple_choice_ikb(large_buttons_data)
    await bot_server.send_photo(callback.from_user.id, group_id, 'main', group_name, ikb)


@dp.callback_query_handler(multiple_choice_cb.filter(filter='unsubscribe'))
async def callback_unsubscribe(callback: types.CallbackQuery) -> None:
    group_id = int(callback.data.split(':')[-1].split('_')[-1])
    database_server.dell_subscription(callback.from_user.id, group_id)
    await callback.answer(Bot_responses['unsubscribe_success_message'], show_alert=True)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@dp.callback_query_handler(multiple_choice_cb.filter(filter='rename_token'))
async def callback_rename_token(callback: types.CallbackQuery) -> None:
    await bot.send_message(callback.from_user.id, config.return_change_token_name(callback.data.split(':')[-1]),
                           parse_mode='HTML')


@dp.callback_query_handler(multiple_choice_cb.filter(filter='choice_token'))
async def callback_choice_token(callback: types.CallbackQuery) -> None:
    data = [int(i) for i in callback.data.split(':')[-1].split('_')]
    await bot_server.processing_choice_subscriber_token(callback.from_user.id, data[0], data[1], callback)


@dp.callback_query_handler(quick_answer_cb.filter())
async def callback_choice_comment(callback: types.CallbackQuery) -> None:
    data = [int(i) for i in callback.data.split(':')[-1].split('_')]
    await bot_server.processing_create_comment(callback.from_user.id, data[0], data[1],
                                               database_server.get_message_by_id(data[2]))


@dp.message_handler(lambda msg: msg.reply_to_message and msg.reply_to_message.from_id == Telegram_bot_id)
async def answer_reply_massage(msg: types.Message) -> None:
    if msg.reply_to_message.text == Bot_responses['add_answer_massage_1']:
        await bot_server.processing_add_message(msg.from_user.id, msg.text)
    elif msg.reply_to_message.text == Bot_responses['add_token_message']:
        await bot_server.processing_add_token(msg.from_user.id, msg.text)

    elif Bot_responses['spoiler'] in msg.reply_to_message.text:
        data = [int(i) for i in msg.reply_to_message.text.split(Bot_responses['spoiler'])[0].split('_')]
        await bot_server.processing_create_comment(msg.from_user.id, data[0], data[1], msg.text)
    elif Bot_responses['spoiler_2'] in msg.reply_to_message.text:
        data = int(msg.reply_to_message.text.split(Bot_responses['spoiler_2'])[0])
        await bot_server.processing_rename_token(msg.from_user.id, data, msg.text)


@dp.message_handler()
async def answer_message(msg: types.Message) -> None:
    if msg.text == Bot_responses['btn_1']:
        buttons_data = [
            [Bot_responses['sett_parse_1'], 'sett_token'],
            [Bot_responses['sett_public_1'], 'sett_public'],
        ]
        await bot.send_message(msg.from_user.id, "Настройка аккаунта",
                               reply_markup=keyboard_generator.create_main_action_ikb(buttons_data))
    elif msg.text == Bot_responses['btn_2']:
        buttons_data = [
            [Bot_responses['dell_answer_1'], 'dell_answer'],
            [Bot_responses['add_answer_1'], 'add_answer'],
            [Bot_responses['manual_1'], 'help'],
        ]
        await bot.send_message(msg.from_user.id, "Настройка ответов",
                               reply_markup=keyboard_generator.create_main_action_ikb(buttons_data))
    elif 'vk.com' in msg.text:
        vk_public_name = msg.text.split('vk.com/')[1].split('?')[0]
        await bot_server.processing_subscription(msg.from_user.id, vk_public_name)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(bot_server.hidden_stream(60, True, 10))
    executor.start_polling(dispatcher=dp, on_startup=on_startup, loop=loop)
