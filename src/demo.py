import requests
import time

# Lock
r = requests.post("http://node1:5000/lock/acquire", json={"resource":"r1","mode":"exclusive"})
print("Node1 acquire lock", r.text)

r = requests.post("http://node2:5000/lock/acquire", json={"resource":"r1","mode":"exclusive"})
print("Node2 try acquire lock (waiting)", r.text)

r = requests.post("http://node1:5000/lock/release", json={"resource":"r1"})
print("Node1 release lock", r.text)

r = requests.post("http://node2:5000/lock/acquire", json={"resource":"r1","mode":"exclusive"})
print("Node2 acquire lock again", r.text)

# Queue
print("Node2 produce message")
rq = requests.post('http://node2:5000/queue/produce', json={'topic':'t','message':'hello'})
print(rq.text)

print("Node3 consume message")
rc = requests.post('http://node3:5000/queue/consume', json={'topic':'t'})
print(rc.text)

# Cache
time.sleep(2) 

print("Node1 write cache")
rw = requests.post('http://node1:5000/cache/write', json={'key':'k1','value':'v1'})
print(rw.text)

print("Node3 read cache")
rread = requests.post('http://node3:5000/cache/read', json={'key':'k1'})
print(rread.text)
