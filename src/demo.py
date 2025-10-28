import requests
import time

# Lock
r = requests.post("http://localhost:5001/lock/acquire", json={"resource":"r1","mode":"exclusive"})
r = requests.post("http://localhost:5002/lock/acquire", json={"resource":"r1","mode":"exclusive"})
r = requests.post("http://localhost:5001/lock/release", json={"resource":"r1"})
r = requests.post("http://localhost:5002/lock/acquire", json={"resource":"r1","mode":"exclusive"})

# Queue
print("Node2 produce message")
rq = requests.post('http://localhost:5002/queue/produce', json={'topic':'t','message':'hello'})
print(rq.text)

print("Node3 consume message")
rc = requests.post('http://localhost:5003/queue/consume', json={'topic':'t'})
print(rc.text)

# Cache
print("Node1 write cache")
rw = requests.post('http://localhost:5001/cache/write', json={'key':'k1','value':'v1'})
print(rw.text)

print("Node3 read cache")
rread = requests.get('http://localhost:5003/cache/read', params={'key':'k1'})
print(rread.text)
