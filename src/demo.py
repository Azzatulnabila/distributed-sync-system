import requests
import time

# Delay supaya semua node siap
print("Waiting for nodes to be ready...")
time.sleep(5)  # 5 detik bisa diubah kalau perlu

# -----------------
# Distributed Lock
# -----------------
print("=== Distributed Lock Demo ===")
r = requests.post("http://node1:5000/lock/acquire", json={"resource":"r1","mode":"exclusive"})
print("Node1 acquire lock:", r.text)

time.sleep(1)  # biar node2 mencoba setelah node1
r = requests.post("http://node2:5000/lock/acquire", json={"resource":"r1","mode":"exclusive"})
print("Node2 try acquire lock (waiting):", r.text)

time.sleep(1)
r = requests.post("http://node1:5000/lock/release", json={"resource":"r1"})
print("Node1 release lock:", r.text)

time.sleep(1)
r = requests.post("http://node2:5000/lock/acquire", json={"resource":"r1","mode":"exclusive"})
print("Node2 acquire lock again:", r.text)

# -----------------
# Distributed Queue
# -----------------
print("\n=== Distributed Queue Demo ===")
time.sleep(1)
print("Node2 produce message")
rq = requests.post('http://node2:5000/queue/produce', json={'topic':'t','message':'hello'})
print(rq.text)

time.sleep(1)
print("Node3 consume message")
rc = requests.post('http://node3:5000/queue/consume', json={'topic':'t'})
print(rc.text)

# -----------------
# Distributed Cache
# -----------------
print("\n=== Distributed Cache Demo ===")
time.sleep(1)
print("Node1 write cache")
rw = requests.post('http://node1:5000/cache/write', json={'key':'k1','value':'v1'})
print(rw.text)

time.sleep(1)
print("Node3 read cache")
rread = requests.get('http://node3:5000/cache/read', params={'key':'k1'})
print(rread.text)
