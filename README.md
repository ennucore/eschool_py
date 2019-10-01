# Eschool

Python library to work with Eschool electronic diary (https://eschool.center)

## Getting Started

Logging in for the first time:

```python
from eschool import EschoolClient


client = EschoolClient.login('your_username', 'your_password')
# you can also write Eschool.login('your_username') and you will be prompted for your password
```

Saving and restoring session:
```python
# Saving:
client.save(filename)
# Restoring:
client = EschoolSession.from_file(filename)
```

Getting marks, homeworks and chats:
```python
client.marks()
client.homeworks()
client.chats()
```
Event handling:
```python
import re


@client.on_message
def process_message(msg):
    print('New message:', re.sub(r'<[^>]*>', '', msg['msg']))   # re to remove markup from message

@client.on_mark
def process_mark(mark):
    print(f'New mark: {mark[0]} for subject {mark[5]}')

@client.on_homework
def process_homework(hw):
    print(f"New homework: {homework[3]} for subject {homework[1]}")
```

### Installing


```bash
sudo pip3 install eschool
```
