import hashlib
import json

from requests import Session
from requests.cookies import cookiejar_from_dict
import getpass


class EschoolBase:
    def __init__(self, cookies=None, handled_homeworks=None, handled_msgs=None, handled_marks=None, filename=None,
                 period='145624', user_id=None):
        self.session = Session()
        if cookies:
            self.session.cookies = cookies
        self.handled_marks = handled_marks or []
        self.handled_msgs = handled_msgs or []
        self.handled_homeworks = handled_homeworks or []
        self.period = period
        self.homework_handler = None
        self.mark_handler = None
        self.message_handler = None
        self.user_id = user_id
        self.filename = filename

    @classmethod
    def login(cls, login, password=None, period='145624', filename=None):
        """
        Login to the account
        """
        self = cls(period=period, filename=filename)
        password = password or getpass.getpass('Eschool password: ')
        password = hashlib.sha256(password.encode()).hexdigest()
        self.session.post('https://app.eschool.center/ec-server/login',
                          data={'username': login,
                                'password': password})
        self.user_id = self.session.get('https://app.eschool.center/ec-server/student/diary').json()['user'][0]['id']
        return self

    def save(self, filename='eschool_account'):
        """
        Save account to file
        :param filename: filename
        """
        self.filename = filename
        with open(filename, 'w') as f:
            f.write(json.dumps(
                (self.session.cookies.get_dict(), self.handled_homeworks, self.handled_msgs, self.handled_marks,
                 self.user_id)))

    @classmethod
    def from_file(cls, filename):
        """
        Restore from file
        :param filename: filename
        :return: session
        """
        with open(filename) as f:
            cookies, homeworks, msgs, marks, user_id = json.loads(f.read())
            cookies = cookiejar_from_dict(cookies)
        self = cls(cookies, homeworks, msgs, marks, filename=filename, user_id=user_id)
        return self

    def get(self, method, prefix='student', **kwargs):
        resp = self.session.get(
            f'https://app.eschool.center/ec-server/{prefix}/{method}/?userId={self.user_id}'
            f'&eiId={self.period}' + ('&' if kwargs else '') + '&'.join(
                [key + '=' + str(kwargs[key]) for key in kwargs.keys() if key != 'prefix']))
        resp.raise_for_status()
        return resp.json()

    def put(self, method, data, url_data='', prefix='chat'):
        resp = self.session.put(
            f'https://app.eschool.center/ec-server/{prefix}/{method}{"?" + url_data if url_data else ""}',
            json.dumps(data))
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
