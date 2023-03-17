import sqlite3 as sq


class DataBaseServer:
    def __init__(self, database_name='database.db') -> None:
        self.database_name = database_name
        self.db = sq.connect(database_name)
        self.cur = self.db.cursor()
        self.create_database()

    def create_database(self) -> None:
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Tokens(token_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL , "
            "user_id INTEGER, token TEXT, token_name TEXT)")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Messages(message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
            " user_id INTEGER, message TEXT)")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Public(public_id INTEGER PRIMARY KEY, public_name TEXT, last_post_id INTEGER)")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Subscriptions(subscription_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
            " user_id INTEGER, public_id INTEGER, token_id INTEGER)")

        self.db.commit()

    def add_subscription(self, user_id, public_id, token_id) -> None:
        self.cur.execute('INSERT INTO Subscriptions(user_id, public_id, token_id) VALUES (?, ?, ?)',
                         [user_id, public_id, token_id])
        self.db.commit()

    def dell_subscription(self, user_id, public_id, check_dell_public=True) -> None:
        self.cur.execute(f'DELETE FROM Subscriptions WHERE user_id={user_id} and public_id={public_id}')
        self.db.commit()
        if check_dell_public and not self.check_have_subscribers_public(public_id):
            self.dell_public(public_id)

    def update_subscription_token_id(self, subscription_id, token_id) -> None:
        self.cur.execute(f"UPDATE Subscriptions SET token_id={token_id} WHERE subscription_id={subscription_id}")
        self.db.commit()

    def get_full_subscriptions_by_user_id(self, user_id) -> list[list[int, int, int, int]] or []:
        subscriptions = self.cur.execute(f"SELECT * FROM Subscriptions WHERE user_id={user_id}").fetchall()
        if subscriptions:
            subscriptions = [[*i] for i in subscriptions]
        return subscriptions

    def get_subscribers_public(self, public_id) -> list[list[int, int]] or []:
        subscribers = self.cur.execute(
            f"SELECT user_id, token_id FROM Subscriptions WHERE public_id={public_id}").fetchall()
        if subscribers:
            subscribers = [[*i] for i in subscribers]
        return subscribers

    def check_have_subscribers_public(self, public_id) -> bool:
        res = self.cur.execute(
            f"SELECT user_id FROM Subscriptions WHERE public_id={public_id}").fetchall()[0]
        if res:
            return True
        return False

    def check_user_subscribers(self, user_id, public_id) -> bool:
        res = self.cur.execute(f"SELECT user_id FROM Subscriptions WHERE public_id={public_id} and user_id={user_id}").fetchall()
        if res:
            return True
        return False

    def add_token(self, user_id, token, token_name) -> None:
        self.cur.execute('INSERT INTO Tokens(user_id, token, token_name) VALUES (?, ?, ?)',
                         [user_id, token, token_name])
        self.db.commit()

    def dell_token_by_id(self, token_id) -> None:
        self.cur.execute(f'DELETE FROM Tokens WHERE token_id={token_id}')
        self.db.commit()

    def update_token_name(self, token_id, token_name) -> None:
        self.cur.execute(f"UPDATE Tokens SET token_name='{token_name}' WHERE token_id={token_id}")
        self.db.commit()

    def check_user_have_token(self, user_id) -> bool:
        token_id = self.cur.execute(f"SELECT token_id FROM Tokens WHERE user_id='{user_id}'").fetchall()
        if token_id:
            return True
        return False

    def check_user_have_this_token(self, user_id, token) -> bool:
        token_id = self.cur.execute(
            f"SELECT token_id FROM Tokens WHERE user_id={user_id} and token='{token}'").fetchall()
        return False

    def get_token_id(self, token, user_id) -> int:
        token_id = self.cur.execute(f"SELECT token_id FROM Tokens WHERE token='{token}'"
                                    f" and user_id={user_id}").fetchall()[0][0]
        return token_id

    def get_token_id_by_public(self, public_id, user_id):
        token_id = self.cur.execute(f"SELECT token_id FROM Subscriptions "
                                    f"WHERE public_id={public_id} and user_id={user_id}").fetchall()[0][0]
        return token_id

    def get_token_name(self, token_id) -> str:
        token_name = self.cur.execute(f"SELECT token_name FROM Tokens WHERE token_id={token_id}").fetchall()[0][0]
        return token_name

    def get_token_by_id(self, token_id) -> str:
        token = self.cur.execute(f"SELECT token FROM Tokens WHERE token_id={token_id}").fetchall()[0][0]
        return token

    def get_tokens_by_user_id(self, user_id) -> list[list[str]] or []:
        tokens = self.cur.execute(f"SELECT token FROM Tokens WHERE user_id={user_id}").fetchall()
        if tokens:
            tokens = [[*i] for i in tokens]
        return tokens

    def get_full_token_by_id(self, token_id) -> list[list, int, str, str]:
        full_token = self.cur.execute(f"SELECT * FROM Tokens WHERE token_id={token_id}").fetchall()[0]
        return [*full_token]

    def get_full_tokens_by_user_id(self, user_id) -> list[list[int, int, str, str]] or []:
        full_tokens = self.cur.execute(f"SELECT * FROM Tokens WHERE user_id={user_id}").fetchall()
        if full_tokens:
            full_tokens = [[*i] for i in full_tokens]
        return full_tokens

    def add_public(self, public_id, public_name, last_post_id) -> None:
        self.cur.execute('INSERT INTO Public(public_id, public_name, last_post_id) VALUES (?, ?, ?)',
                         [public_id, public_name, last_post_id])
        self.db.commit()

    def dell_public(self, public_id) -> None:
        self.cur.execute(f'DELETE FROM Public WHERE public_id={public_id}')
        self.db.commit()

    def check_have_public_by_id(self, public_id) -> bool:
        public = self.cur.execute(f"SELECT public_id FROM Public WHERE public_id='{public_id}'").fetchall()
        if public:
            return True
        return False

    def update_public_last_post_id(self, public_id, last_post_id) -> None:
        self.cur.execute(f"UPDATE Public SET last_post_id={last_post_id} WHERE public_id={public_id}")
        self.db.commit()

    def update_public_name(self, public_id, public_name) -> None:
        self.cur.execute(f"UPDATE Public SET public_name='{public_name}' WHERE public_id={public_id}")
        self.db.commit()

    def get_all_public(self) -> list[list[int, str, int]] or []:
        all_public = self.cur.execute(f"SELECT * FROM Public").fetchall()
        if all_public:
            all_public = [[*i] for i in all_public]
        return all_public

    def get_public_name_by_id(self, public_id) -> str:
        public_name = self.cur.execute(f"SELECT public_name FROM Public WHERE public_id={public_id}").fetchall()[0][0]
        return public_name

    def get_public_by_user_id(self, user_id) -> list[list[int, str]] or []:
        groups = self.cur.execute(f"SELECT public_id FROM Subscriptions WHERE user_id={user_id} ").fetchall()
        group_id = ', '.join([str(i[0]) for i in groups])
        public = self.cur.execute(
            f'SELECT public_id,public_name FROM Public WHERE public_id IN ({group_id}) ').fetchall()
        if public:
            public = [[*i] for i in public]
        return public

    def add_message(self, user_id, message) -> None:
        self.cur.execute('INSERT INTO Messages(user_id, message) VALUES (?, ?)',
                         [user_id, message])
        self.db.commit()

    def dell_message_by_id(self, message_id) -> None:
        self.cur.execute(f'DELETE FROM Messages WHERE message_id={message_id}')
        self.db.commit()

    def get_message_by_id(self, message_id) -> str:
        message = self.cur.execute(f"SELECT message FROM Messages WHERE message_id={message_id}").fetchall()[0][0]
        return message

    def get_full_messages_by_user_id(self, user_id) -> list[list[int, str]] or []:
        messages = self.cur.execute(f"SELECT message_id, message FROM Messages WHERE user_id={user_id}").fetchall()
        if messages:
            messages = [[*i] for i in messages]
        return messages
