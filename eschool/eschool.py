import time
import traceback
from threading import Thread

from .eschool_base import EschoolBase


class EschoolClient(EschoolBase):
    """
    Eschool client
    """
    def diary_units(self) -> dict:
        """
        Get diary units (subjects)
        """
        return self.get('getDiaryUnits')

    def marks(self) -> list:
        """
        Get all marks for current period
        :return: list of marks in format:
        [mark value (1,2,3,4,5), mark weight, mark date, lesson (where mark is) id, work name (homework, exam etc),
        lesson name (Algebra etc)]] for  each mark
        """
        result = self.get('getDiaryPeriod')['result']
        units = {unit['unitId']: unit['unitName'] for unit in result}
        return [[lesson['markVal'], lesson['mktWt'], lesson['startDt'], lesson['lessonId'], lesson['lptName'],
                 units[lesson['unitId']]]
                for lesson in result if lesson.get('markVal')]

    def diary(self, d1=None, d2=None):
        """
        Get diary (all lessons)
        :param d1: start date (format - time seconds since the Epoch)
        :param d2:
        :return: list of lessons (each lesson is a dictionary)
        """
        return self.get('diary', d1=(d1 or int(time.time() - 48 * 3600)) * 1000,
                        d2=(d2 or int((d1 or int(time.time() - 48 * 3600)) + 14 * 24 * 3600)) * 1000)['lesson']

    def homeworks(self, d1=None, d2=None):
        """
        Get all homeworks from d1 to d2
        :return: list of homeworks:
        [homework id, lesson name, lesson date, homework text, [file id, filename] for each attachment]
            for each homework
        """
        result = []
        for lesson in self.diary(d1, d2):
            part = list(filter(lambda part: len(part['variant']), lesson.get('part')))
            if not part:
                continue
            part = part[0]
            if not (part['variant'][0].get('text') or part['variant'][0].get('file')):
                continue
            result.append([part['variant'][0]['id'], lesson['unit']['name'], lesson['date'],
                           part['variant'][0].get('text'),
                           [[file['id'], file['fileName']] for file in part['variant'][0]['file']]])
        return result

    def chats(self, chat_count=250):
        """
        Get first chat_count chats
        :return: list of chats (each chat is a dictionary)
        """
        return self.get('threads', prefix='chat', newOnly='false', row=1, rowsCount=chat_count)

    def messages(self, thread_id):
        """
        Get messages from thread with thread_id
        :return: list of messages (dictionaries)
        """
        return self.get('messages', prefix='chat', getNew='false', isSearch='false', rowStart=1, rowsCount=3,
                        threadId=thread_id)

    def chat_members(self, thread_id):
        """
        Get list of chat members
        :param thread_id: id of the chat
        :return: list of members
        """
        return self.get('mem_and_cnt', prefix='chat', threadId=thread_id)['members']

    def get_groups(self):
        """
        Get all available groups
        :return: list of groups
        """
        return self.get('olist', prefix='usr')

    def handling(self):
        """
        Start handling events
        """
        self.handled_homeworks = self.handled_homeworks or [homework[0] for homework in self.homeworks()]
        self.handled_msgs = self.handled_msgs or \
                            [msg['msgId'] for chat in self.chats() for msg in self.messages(chat['threadId'])]
        self.handled_marks = self.handled_marks or [mark[3] for mark in self.marks()]

        def homeworks_and_marks():
            while True:
                try:
                    if self.homework_handler:
                        homeworks = self.homeworks()
                        for homework in homeworks:
                            if homework[0] not in self.handled_homeworks:
                                self.homework_handler(homework)
                                self.handled_homeworks.append(homework[0])
                    if self.mark_handler:
                        marks = self.marks()
                        for mark in marks:
                            if mark[3] not in self.handled_marks:
                                self.mark_handler(mark)
                                self.handled_marks.append(mark[3])
                    time.sleep(60 * 3)
                except Exception as e:
                    print(f'time: {time.time()}, exception: {"".join(traceback.format_tb(e.__traceback__))}')
                if self.filename:
                    self.save()

        def messages_loop():
            while True:
                try:
                    msgs = list(filter(lambda msg: msg['msgId'] not in self.handled_msgs,
                                       [msg for chat in self.chats() for msg in
                                        self.messages([chat['threadId'], time.sleep(30)][0])]))
                    for msg in reversed(msgs):
                        self.handled_msgs.append(msg['msgId'])
                        self.message_handler(msg)
                    time.sleep(60 * 3)
                except Exception as e:
                    print('exception:', e)
                if self.filename:
                    self.save()

        Thread(target=homeworks_and_marks).start()
        if self.message_handler:
            Thread(target=messages_loop).start()
        while True:
            pass
