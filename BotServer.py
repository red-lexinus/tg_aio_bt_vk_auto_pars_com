import aiogram
import os
import requests
import asyncio
import time
from aiogram.types import MediaGroup, InputFile, Message
from aiogram.utils.markdown import hspoiler

from KeyboardGenerator import KeyboardGenerator
from DataBaseServer import DataBaseServer
from VkParser import VkParser


class BotServer:
    def __init__(self, bot: aiogram.Bot, db: DataBaseServer, vk_parser: VkParser, keyboard_generator: KeyboardGenerator,
                 standard_answer: dict, file_directory: str = '', posts_storage_channel: int = -1001954413154):
        self.vk_parser = vk_parser
        self.keyboard_generator = keyboard_generator
        self.bot = bot
        self.db = db
        self.standard_answer = standard_answer
        self.file_directory = file_directory
        self.posts_storage_channel = posts_storage_channel

    async def processing_command_start(self, user_id, user_name):
        await self.bot.send_message(user_id, f"{user_name} {self.standard_answer['start_massage']}",
                                    reply_markup=self.keyboard_generator.create_start_command_ikb(
                                        [self.standard_answer['btn_1'], self.standard_answer['btn_1']]))

    async def processing_add_token(self, user_id, token, standard_token_name='акк'):
        if self.vk_parser.check_correct_token(token):
            if self.db.check_user_have_this_token(user_id, token):
                await self.bot.send_message(user_id, self.standard_answer['correct_token_2'])
            else:
                self.db.add_token(user_id, token, standard_token_name)
                token_id = self.db.get_token_id(token, user_id)
                buttons_data = [
                    [self.standard_answer['change_token_name_1'], 'rename_token', f'{token_id}']
                ]
                await self.bot.send_message(user_id, self.standard_answer['correct_token_1'] + standard_token_name,
                                            reply_markup=self.keyboard_generator.create_multiple_choice_ikb(
                                                buttons_data))
        else:
            await self.bot.send_message(user_id, self.standard_answer['invalid_token_1'])

    async def processing_rename_token(self, user_id, token_id, token_name):
        self.db.update_token_name(token_id, token_name)
        await self.bot.send_message(user_id, self.standard_answer['success_rename_token_massage'])

    async def processing_create_comment(self, user_id, public_id, post_id, message):
        token_id = self.db.get_token_id_by_public(public_id, user_id)
        if self.vk_parser.add_comment(public_id, post_id, message, self.db.get_token_by_id(token_id)):
            await self.bot.send_message(user_id, self.standard_answer['post_comment_success_message'])
        else:
            await self.bot.send_message(user_id, self.standard_answer['post_comment_failure_message'])

    async def processing_choice_subscriber_token(self, user_id, public_id, token_id, callback):
        if self.db.check_user_subscribers(user_id, public_id):
            if callback:
                await callback.answer(self.standard_answer['already_signed_by_group'], show_alert=True)
        else:
            self.db.add_subscription(user_id, public_id, token_id)
            if not self.db.check_have_public_by_id(public_id):
                token = self.db.get_token_by_id(token_id)
                group_info = self.vk_parser.get_info_group(public_id, token)
                last_id = self.vk_parser.get_group_last_id(public_id, token)
                self.db.add_public(public_id, group_info[1], last_id)
            if callback:
                await callback.answer(self.standard_answer['success_sub_1'], show_alert=True)

    async def processing_subscription(self, user_id, public_name):
        tokens = [[i[0]] for i in self.db.get_tokens_by_user_id(user_id)]
        tokens += [self.vk_parser.standard_token]
        parser_token = ''
        if tokens:
            for token in tokens:
                if self.vk_parser.check_correct_token(token[0], public_name):
                    parser_token = token[0]
                    break
        if parser_token:
            group_data = self.vk_parser.get_info_group(public_name, parser_token)
            self.save_photo(group_data[-1], group_data[0], 'main')
            if group_data:
                if self.db.check_user_subscribers(user_id, group_data[0]):
                    await self.bot.send_message(user_id, self.standard_answer['already_signed_by_group'])
                else:
                    data = self.db.get_full_tokens_by_user_id(user_id)
                    buttons_data = [
                        [self.standard_answer['choice_token_1'] + d[3], 'choice_token', f'{group_data[0]}_{d[0]}'] for d
                        in data
                    ]
                    ikb = self.keyboard_generator.create_multiple_choice_ikb(buttons_data)
                    await self.send_photo(user_id, group_data[0], 'main', group_data[1], ikb)
        else:
            await self.bot.send_message(user_id, self.standard_answer['invalid_url_vk'])

    async def save_post_in_storage_channel(self, kwargs: dict[any]):
        need_teg = [
            'public_name', 'post_date', 'copy_history_flag', 'media_message', 'storage_post_id'
        ]
        if not all(teg in kwargs for teg in need_teg):
            raise Exception('Нет нужных ключей')

        post_start_message = self.constructs_post_start_message(kwargs['public_name'], kwargs['post_date'],
                                                                kwargs['copy_history_flag'])
        reply_message_id = {}
        forwarded_post_id = self.db.get_storage_post_info(kwargs['storage_post_id'])['forwarded_post_id']
        if forwarded_post_id:
            arr = self.db.get_storage_message_by_post_id(forwarded_post_id)
            if len(arr) > 1:
                reply_message_id['reply_to_message_id'] = arr[1]['storage_message_id']
        message_n = 1
        if len(kwargs['media_message'][0].media) > 0:
            message = await self.bot.send_message(self.posts_storage_channel, post_start_message)
            self.db.add_storage_message(message.message_id, kwargs['storage_post_id'], message_n)
            message_n += 1
            message = await self.bot.send_media_group(self.posts_storage_channel, kwargs['media_message'][0],
                                                      **reply_message_id)
            message = message[0]
            self.db.add_storage_message(message.message_id, kwargs['storage_post_id'], message_n)
            for post_message in kwargs['media_message'][3]:
                message = await self.bot.send_message(self.posts_storage_channel, post_message,
                                                      reply_to_message_id=message.message_id)
                message_n += 1
                self.db.add_storage_message(message.message_id, kwargs['storage_post_id'], message_n)

        elif kwargs['media_message'][1]:
            message = await self.bot.send_message(self.posts_storage_channel, post_start_message)
            self.db.add_storage_message(message.message_id, kwargs['storage_post_id'], message_n)
            message_n += 1
            message = await self.bot.send_message(self.posts_storage_channel, kwargs['media_message'][1][0],
                                                  **reply_message_id)
            self.db.add_storage_message(message.message_id, kwargs['storage_post_id'], message_n)
            for post_message in kwargs['media_message'][3]:
                message = await self.bot.send_message(self.posts_storage_channel, post_message,
                                                      reply_to_message_id=message.message_id)
                message_n += 1
                self.db.add_storage_message(message.message_id, kwargs['storage_post_id'], message_n)

    async def repost_messages_to_user(self, storage_post_id: int, user_id: int):
        repost_messages = []
        quick_answers = self.db.get_full_messages_by_user_id(user_id)
        storage_post_info = self.db.get_storage_post_info(storage_post_id)
        ikb = self.keyboard_generator.create_quick_answer_ikb(quick_answers, storage_post_info['public_id'],
                                                              storage_post_info['post_id'])
        t = hspoiler(f"{storage_post_info['public_id']}_{storage_post_info['post_id']}⁤")
        text = f'{t}\nНаписать сообщение' \
               f' в комменты можно также ответив на это сообщение'
        kwargs = {
            'chat_id': user_id, 'text': text, 'reply_markup': ikb, 'parse_mode': 'HTML'
        }
        if storage_post_info['forwarded_post_id']:
            repost_messages += self.db.get_storage_message_by_post_id(storage_post_info['forwarded_post_id'])
        repost_messages += self.db.get_storage_message_by_post_id(storage_post_id)
        for i in range(len(repost_messages)):
            await self.bot.forward_message(user_id, self.posts_storage_channel,
                                           repost_messages[i]['storage_message_id'], protect_content=False)
        if len(repost_messages):
            await self.bot.send_message(**kwargs)

    async def send_post_user(self, user_id, public_id, post_id, media_message, post_date, copy_history_flag=False,
                             reply_media_message=None, reply_post_date=None, reply_public_name=None):
        reply_storage_post_id = None
        messages = self.db.get_full_messages_by_user_id(user_id)
        ikb = self.keyboard_generator.create_quick_answer_ikb(messages, public_id, post_id)
        text = f'{hspoiler(f"{public_id}_{post_id}⁤")}\nНаписать сообщение' \
               f' в комменты можно также ответив на это сообщение'
        args_2 = {
            'chat_id': user_id, 'text': text, 'reply_markup': ikb, 'parse_mode': 'HTML'
        }
        args = {'chat_id': user_id, 'media': media_message[0]}
        if copy_history_flag:
            reply_storage_post_id = self.db.add_storage_post(public_id, post_id)
            if reply_storage_post_id != 0:
                kwargs = {
                    'storage_post_id': reply_storage_post_id, 'public_name': reply_public_name,
                    'post_date': reply_post_date, 'media_message': reply_media_message, 'copy_history_flag': True
                }
                await self.save_post_in_storage_channel(kwargs)
            # reply_message = 0
            # reply_post_start_message = self.constructs_post_start_message(reply_public_name, reply_post_date, True)
            # if len(reply_media_message[0].media) > 0:
            #     await self.bot.send_message(user_id, reply_post_start_message)
            #     reply_message = await self.bot.send_media_group(user_id, reply_media_message[0])
            #     reply_message = reply_message[0]
            #     for post_message in reply_media_message[3]:
            #         reply_message = await self.bot.send_message(user_id, post_message,
            #                                                     reply_to_message_id=reply_message.message_id)
            #
            # elif reply_media_message[1]:
            #     await self.bot.send_message(user_id, reply_post_start_message)
            #     reply_message = await self.bot.send_message(user_id, reply_media_message[1][0])
            # if reply_message:
            #     args['reply_to_message_id'] = reply_message.message_id

        ###
        storage_post_id = self.db.add_storage_post(public_id, post_id)
        if storage_post_id != 0:
            kwargs = {
                'storage_post_id': storage_post_id, 'public_name': self.db.get_public_name_by_id(public_id),
                'post_date': post_date, 'media_message': media_message, 'copy_history_flag': False
            }
            await self.save_post_in_storage_channel(kwargs)
        ###

        # start_message = self.constructs_post_start_message(self.db.get_public_name_by_id(public_id), post_date)
        # if len(media_message[0].media) > 0:
        #     await self.bot.send_message(user_id, start_message)
        #     reply_message = await self.bot.send_media_group(**args)
        #     reply_message = reply_message[0]
        #     for post_message in media_message[3]:
        #         reply_message = await self.bot.send_message(user_id, post_message,
        #                                                     reply_to_message_id=reply_message.message_id)
        #
        #     await self.bot.send_message(**args_2)
        # elif media_message[1]:
        #     args['text'] = media_message[1][0]
        #     args.pop('media')
        #     await self.bot.send_message(user_id, start_message)
        #     reply_message = await self.bot.send_message(**args)
        #     for post_message in media_message[3]:
        #         reply_message = await self.bot.send_message(user_id, post_message,
        #                                                     reply_to_message_id=reply_message.message_id)
        #     await self.bot.send_message(**args_2)

    async def mailing_posts(self, public_id, posts, users_data, token, db_update=True):
        if db_update:
            max_id = max([i['id'] for i in posts])
            self.db.update_public_last_post_id(public_id, max_id)
        for post_num in range(len(posts)):
            reply_storage_post_id = None
            if 'copy_history' in posts[post_num]:
                reply_storage_post_id = self.db.get_storage_post_id(-posts[post_num]['copy_history']['owner_id'],
                                                                    posts[post_num]['id'])
                if reply_storage_post_id == 0:
                    try:
                        reply_public_info_data = self.vk_parser.get_info_group(
                            -posts[post_num]['copy_history']['owner_id'],
                            token)
                        reply_public_name = reply_public_info_data[1]
                    except BaseException:
                        reply_public_name = '(страницы пользователя)'
                    reply_post_date = posts[post_num]['copy_history']['date']
                    reply_media_message = self.return_media_message(posts[post_num]['copy_history'],
                                                                    -posts[post_num]['copy_history']['owner_id'])
                    reply_storage_post_id = self.db.add_storage_post(-posts[post_num]['copy_history']['owner_id'],
                                                                     posts[post_num]['id'])
                    reply_kwargs = {
                        'public_name': reply_public_name, 'storage_post_id': reply_storage_post_id,
                        'copy_history_flag': True, 'post_date': reply_post_date, 'media_message': reply_media_message
                    }
                    await self.save_post_in_storage_channel(reply_kwargs)

            post_id = posts[post_num]['id']
            media_message = self.return_media_message(posts[post_num], public_id)
            post_date = posts[post_num]['date']
            ####
            storage_post_id = self.db.get_storage_post_id(public_id, post_id)
            if storage_post_id == 0:
                storage_post_id = self.db.add_storage_post(public_id, post_id, reply_storage_post_id)
                kwargs = {
                    'storage_post_id': storage_post_id, 'copy_history_flag': False, 'media_message': media_message,
                    'post_date': post_date, 'public_name': self.db.get_public_name_by_id(public_id)
                }
                await self.save_post_in_storage_channel(kwargs)

            for user in users_data:
                user_id = user[0]
                await self.repost_messages_to_user(storage_post_id, user_id)

    async def hidden_stream(self, min_time_sleep=60, running=True, count_posts_check=3):
        await asyncio.sleep(5)
        while running:
            time_start_cycle = time.time()
            ####
            all_public = self.db.get_all_public()
            for n_public in range(len(all_public)):
                subscribers = self.db.get_subscribers_public(all_public[n_public][0])
                if subscribers:
                    public_id, token = all_public[n_public][0], self.db.get_token_by_id(subscribers[0][1])
                    new_posts = self.vk_parser.get_new_post(public_id, all_public[n_public][2], token,
                                                            count_posts_check)
                    if new_posts:

                        # отправка этих постов всем пользователям
                        await self.mailing_posts(public_id, new_posts, subscribers,
                                                 token=self.db.get_token_by_id(subscribers[0][1]))
                        ####
            time_end_cycle = time.time()
            if time_end_cycle - time_start_cycle < min_time_sleep:
                await asyncio.sleep(min_time_sleep - time_end_cycle + time_start_cycle)

    async def get_manual_token_message(self, user_id):
        media = MediaGroup()
        photos = [
            '1', '2', '3', '4', '5'
        ]
        for photo in photos:
            media.attach_photo(
                InputFile(f"{self.file_directory}instructions/{photo}.png"))
        media.media[0].caption = self.standard_answer['manual_get_token_message']
        await self.bot.send_media_group(user_id, media=media)

    async def processing_add_message(self, user_id, message):
        self.db.add_message(user_id, message)
        await self.bot.send_message(user_id, self.standard_answer['massage_1'])

    async def send_photo(self, chat_id, group_id, photo_id, caption, ikb):
        await self.bot.send_photo(chat_id, open(f"{self.file_directory}files/{group_id}/{photo_id}.jpg", 'rb'),
                                  caption=f"{caption}", reply_markup=ikb)

    def save_photo(self, url, group_id, photo_id) -> str or bool:
        try:
            res = requests.get(url)
            if not os.path.exists(f"{self.file_directory}files/{group_id}"):
                os.mkdir(f"{self.file_directory}files/{group_id}/")
            files = os.listdir(f"{self.file_directory}files/{group_id}/")
            if f"{self.file_directory}files/{group_id}/{photo_id}.jpg" in files:
                return f"{self.file_directory}files/{group_id}/{photo_id}.jpg"
            with open(f"{self.file_directory}files/{group_id}/{photo_id}.jpg", "wb") as img_file:
                img_file.write(res.content)
            return f"{self.file_directory}files/{group_id}/{photo_id}.jpg"
        except Exception:
            return False

    def return_media_message(self, post, group_id):
        media = MediaGroup()
        res = [media, [], [], []]
        if 'attachments' in post:
            for element in post['attachments']:
                if element['type'] == 'photo':
                    photos = sorted(element['photo']['sizes'], key=lambda d: d['height'] and d['width'])
                    media.attach_photo(
                        InputFile(self.save_photo(photos[-1]['url'], group_id, element['photo']['id'])))
                elif element['type'] == 'video':
                    ###1!!!
                    video_element = element['video']
                    res[2].append(
                        f'https://vk.com/group_name?z=video{video_element["owner_id"]}_{video_element["id"]}')
                    res[2].append(f'owner_id id')
                try:
                    if len(post['text']) > 1024:
                        media.media[0].caption = post['text'][0:1024]
                        t = post['text'][1024:1024 * 5]
                        for i in range(1 + len(t) // (1024 * 4)):
                            res[3].append(t[i * (1024 * 4):(i + 1) * (1024 * 4)])
                    else:
                        media.media[0].caption = post['text']
                except:
                    pass
        if 'text' in post and post['text']:
            if len(post['text']) > 1024 * 4:
                res[1].append(post['text'][0:1024 * 4])
                t = post['text'][1024 * 4:1024 * 8]
                for i in range(1 + len(t) // (1024 * 4)):
                    res[3].append(t[i * (1024 * 4):(i + 1) * (1024 * 4)])
            else:
                res[1].append(post['text'])
        if 'copy_history' in post:
            res[2].append('-' * 5 + 'Упоминание другого поста' + '-' * 5)
        return res

    def constructs_post_start_message(self, public_name: str, post_time: int, post_reply_flag=False) -> str:
        t = time.gmtime(post_time)
        if not post_reply_flag:
            return f'{public_name} пост вышел {t.tm_mday}-{t.tm_mon}-{t.tm_year % 100} в {t.tm_hour}-{t.tm_min}'
        return f'Пост пересланный из {public_name} вышедший {t.tm_mday}-{t.tm_mon}-{t.tm_year % 100} в {t.tm_hour}-{t.tm_min}'
