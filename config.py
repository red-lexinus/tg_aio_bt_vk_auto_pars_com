from aiogram.utils.markdown import hspoiler

Telegram_Token = '5672852233:AAHhH5WnMUmSAtCzMwO_sieDIj_saipxfcY'
Telegram_bot_id = 5672852233
DB_name = 'database.db'
Bot_responses = {
    'spoiler': '⁤',
    'spoiler_2': '‍',
    'start_massage': ', приветсвую вас. Данный бот позволит вам быстро коменнтировать новые посты в пабликах ВК',
    'dell_answer_1': 'Удалить существующие ответы',
    'dell_answer_2': 'Удалить ответ',
    'dell_answer_3': 'Ответ успешно удалён',
    'add_answer_1': 'Добавить новый ответ',
    'manual_1': 'Инструкция',
    'manual_massage_1': 'Настраеваемые ответы будут предлагаться под каждым постом. Также вы можете отвечат'
                        ' на каждый пост индивидуально, просто "ответьте" на пост нужным комментом',
    'add_answer_massage_1': 'Напишите новый вариант комментария в ответ на это сообщение',
    'sett_parse_1': 'Ключ парсера ВК',
    'sett_public_1': 'Паблики ВК',
    'btn_1': 'Настроить аккаунт парсинга',
    'btn_2': 'Настроить варианты ответов',
    'massage_1': 'Вы успешно добавили новый вариант ответа',
    'add_token_message': 'Отправьте ваш token ответом на это сообшение',
    'help_get_token_1': 'типо описание как сделать норм настройку',
    'settings_public_1': 'Ваши паблики',
    'correct_token_1': 'Вы успешно добавили свой токен! Токен будет иметь следующее сокращённое имя: ',
    'correct_token_2': 'Но вы уже сохранили этот токен, что с вами?',
    'invalid_token_1': 'К сожалению данный токен не работает',
    'change_token_name_1': 'поменять сокращённое имя токена',
    'choice_token_1': 'Подписаться через ',
    'success_sub_1': 'Вы успешно подписались на паблик',
    'need_token_1': 'Для начала создайте себе token! без него бот работать будет не в состоянии!',
    'get_token_manual_button': 'Как получить рабочий токен',
    'get_token_url_button': 'Создать токен',
    'get_token_url_message': 'После создания токена, отправьте его сообшение в ответе на это сообщение',
    'get_token_url': 'https://vkhost.github.io/',
    'add_token_button': 'Добавить токен в бота',
    'setting_public_message_1': 'Если хотите просмотреть базовую информацию о группе, нажмите на кнопку'
                                ', Если хотите подписаться на новый паблик киньте на него ссылку',
    'setting_public_message_2': 'Вы не подписаны ни на одну из групп, чтобы подписаться отправьте ссылку на группу',
    'unsubscribe_button': 'Отписаться от рассылки на паблик',
    'get_1_post_button': 'посмотреть последний пост',
    'get_5_post_button': 'посмотреть последнии посты',
    'post_comment_success_message': 'Вы успешно оставили свой комментарий',
    'post_comment_failure_message': 'Почему-то не удалось оставить комментарий!',
    'unsubscribe_success_message': 'Вы успешно отписались',
    'already_signed_by_group': 'Но вы уже подписанны на эту группу',
    'dell_token_button': 'Удалить ненужный токен',
    'rename_token_button': 'Переименовать краткое имя токена',
    'dell_token_message': 'Какие токены вы хотите удалить',
    'rename_token_message': 'Какие токены вы хотите переименовать',
    'success_rename_token_massage': 'Вы удачно поменяли название для токена!',
    'dell_token_success_message': 'Вы удачно удалили токен',
    'invalid_url_vk': 'К сожалению не получилось запарсить эту группу',
    'manual_get_token_message': '1) Нажмите на кнопку "Создать токен"\n2) повторяйте за фотографиями\n'
                                '3) скопируйте ссылку корректно и добавьте её в бота',

}

vk_standard_token = 'vk1.a.hXGwmFB9tAOv1ja7rkz91fgKS8o5OIaP1a62zd2OLTJOSV8Bq19CWKtcwInUmAklsA_RSaBGJ0kamvUAG2Kemo39VykdmZdaH9q523j8WC05ZUkHuqAGlS2CJqxdfJModcyFXELKxZfR7Q3zo_6V5CNyq4Zhvwr_Qph4VlWpKg18gGCBIgt4RD0lMk5kRdAcpKOf1UPAaUlSESMAhqRKmA'

chanel_id = -1001954413154


def return_changeable_message(group_id, post_id):
    text = hspoiler(f"{group_id}_{post_id}⁤")
    return f'{text}\nНаписать сообщение в комменты можно также ответив на это сообщение'


def return_change_token_name(token_id):
    text = hspoiler(f"{token_id}‍")
    return f'{text}\nНаписать новое сокращённое название для токена можно ответив на это сообщение'
