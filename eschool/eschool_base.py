import hashlib
import json

from requests import Session
import getpass


class EschoolBase:
    def __init__(self, login=None, password=None, handled_homeworks=None, handled_msgs=None, handled_marks=None,
                 filename=None, period='145624', user_id=None):
        self.username = login
        self.session = Session()
        self.password = password
        self.handled_marks = handled_marks or []
        self.handled_msgs = handled_msgs or []
        self.handled_homeworks = handled_homeworks or []
        self.period = period
        self.homework_handler = None
        self.mark_handler = None
        self.message_handler = None
        self.user_id = user_id
        self.filename = filename

    def auth(self):
        self.session.post('https://app.eschool.center/ec-server/login',
                          data={'username': self.username,
                                'password': self.password})
        self.user_id = self.session.get('https://app.eschool.center/ec-server/student/diary').json()['user'][0]['id']

    @classmethod
    def login(cls, login, password=None, period='145624', filename=None):
        """
        Login to the account
        """
        self = cls(period=period, filename=filename)
        password = password or getpass.getpass('Eschool password: ')
        self.username = login
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.auth()
        return self

    def save(self, filename='eschool_account'):
        """
        Save account to file
        :param filename: filename
        """
        self.filename = filename
        with open(filename, 'w') as f:
            f.write(json.dumps(((self.username, self.password), self.handled_homeworks, self.handled_msgs,
                                self.handled_marks, self.user_id)))

    @classmethod
    def from_file(cls, filename):
        """
        Restore from file
        :param filename: filename
        :return: session
        """
        with open(filename) as f:
            (login, password), homeworks, msgs, marks, user_id = json.loads(f.read())
        self = cls(login, password, homeworks, msgs, marks, filename=filename, user_id=user_id)
        return self

    def get(self, method, prefix='student', **kwargs):
        resp = self.session.get(
            f'https://app.eschool.center/ec-server/{prefix}/{method}/?userId={self.user_id}'
            f'&eiId={self.period}' + ('&' if kwargs else '') + '&'.join(
                [key + '=' + str(kwargs[key]) for key in kwargs.keys() if key != 'prefix']))
        if resp.status_code == 401:
            self.auth()
            return self.get(method, prefix, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def put(self, method, data, url_data='', prefix='chat'):
        resp = self.session.put(
            f'https://app.eschool.center/ec-server/{prefix}/{method}{"?" + url_data if url_data else ""}',
            json.dumps(data))
        if resp.status_code == 401:
            self.auth()
            return self.put(method, data, url_data, prefix)
        resp.raise_for_status()
        return resp.json()

    def on_homework(self, func):
        """
        Decorator for handling event (adding homework)
        """
        self.homework_handler = func

    def on_mark(self, func):
        """
        Decorator for handling event (adding mark)
        """
        self.mark_handler = func

    def on_message(self, func):
        """
        Decorator for handling event (adding message)
        """
        self.message_handler = func

    def download_file(self, file_id):
        """
        Download file with file_id
        :param file_id: file id
        :return: raw file content (bytes)
        """
        result = self.session.get(f'https://app.eschool.center/ec-server/files/{file_id}')
        return result.content
