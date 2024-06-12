import uuid

print(uuid.uuid4())

from queue import Queue

q = Queue(5)

for i in range(6):
    try:
        print('put', i)
        q.put(i, block=False)
    except:
        print('Queue is full')
        break
