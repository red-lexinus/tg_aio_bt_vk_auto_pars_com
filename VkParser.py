import requests


class VkParser:
    def __init__(self, standard_token: str, start_link: str = 'https://api.vk.com/method/',
                 version: str = 'v=5.131') -> None:
        self.standard_token = standard_token
        self.start_link = start_link
        self.version = version

    def add_comment(self, group_id, post_id, message, token) -> bool:
        link = f"{self.start_link}wall.createComment?owner_id={-group_id}&" \
               f"post_id={post_id}&access_token={token}&message={message}&{self.version}"
        req = requests.get(link).json()
        if 'error' in req:
            return False
        return True

    def get_info_group(self, group_id, token) -> list[int, str, str, str] or bool:
        link = f"{self.start_link}groups.getById?" \
               f"group_id={group_id}&access_token={token}&{self.version}"
        req = requests.get(link).json()
        if 'response' in req and len(req['response']) > 0:
            group_info = req['response'][0]
            return [group_info['id'], group_info['name'], group_info['screen_name'], group_info['photo_200']]
        return False

    def get_post_by_id(self, group_id, post_id, token) -> dict[any] or bool:
        # !!!!! перепроверь!!!
        link = f'{self.start_link}wall.getById?posts={-group_id}_{post_id}&extended=0&' \
               f'copy_history_depth=2&access_token={token}&{self.version}'
        req = requests.get(link).json()
        if 'error' in req or req['response'] == []:
            return False
        js_storage = req['response'][0]
        post = {}
        teg = ['id', 'text', 'attachments', 'owner_id', 'date']
        for el in teg:
            if el in js_storage:
                post[el] = js_storage[el]
        if 'copy_history' in js_storage:
            reply_post = {}
            for t_2 in teg:
                if t_2 in js_storage:
                    reply_post[t_2] = js_storage['copy_history'][0][t_2]
            post['copy_history'] = reply_post
        return post

    def get_new_post(self, group_id, last_id, token, count_post=5) -> list[dict[any]] or []:
        # !!!!!
        link = f"{self.start_link}wall.get?" \
               f"owner_id={-group_id}&count={count_post}&access_token={token}&{self.version}"
        try:
            req = requests.get(link).json()['response']['items']
            if 'is_pinned' in req[0]:
                if req[0]['id'] < last_id:
                    req = req[1::]
            posts = []
            teg = ['id', 'text', 'attachments', 'date', 'owner_id']
            for i in range(len(req)):
                if req[i]['id'] > last_id:
                    post = {}
                    for t in teg:
                        if t in req[i]:
                            post[t] = req[i][t]
                    if 'copy_history' in req[i]:
                        reply_post = {}
                        for t_2 in teg:
                            if t_2 in req[i]:
                                reply_post[t_2] = req[i]['copy_history'][0][t_2]
                        post['copy_history'] = reply_post
                    posts.append(post)

                else:
                    return posts
            return posts
        except IndexError or KeyError:
            return []

    def check_group_fixed_post(self, group_id, token) -> bool:
        # !!!!!!!!
        link = f"{self.start_link}wall.get?" \
               f"owner_id={-group_id}&count=1&access_token={token}&{self.version}"
        js_storage = requests.get(link).json()['response']['items'][0]
        if 'is_pinned' in js_storage:
            return True
        return False

    def get_group_last_id(self, group_id, token) -> int:
        # !!!!
        link = f"{self.start_link}wall.get?" \
               f"owner_id={-group_id}&count=2&access_token={token}&{self.version}"
        req = requests.get(link).json()['response']['items']
        res = 0
        for i in req:
            res = max(i['id'], res)
        return res

    def check_correct_token(self, token, group_name='vk'):
        link = f"{self.start_link}wall.get?" \
               f"domain={group_name}&count={1}&access_token={token}&{self.version}"
        if 'error' in requests.get(link).json():
            return False
        return True
