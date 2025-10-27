# Architecture - Distributed Synchronization System (Azzatul Nabila)

## Ringkasan
Sistem terdiri dari:
- 3 Node aplikasi (node1, node2, node3)
- 1 Redis server (persistence + pub/sub)
Fungsi utama: Lock Manager (Raft leader), Persistent Queue (Redis), Cache (LRU + invalidation via Redis pub/sub).

## Diagram (mermaid)
```mermaid
flowchart LR
  subgraph Cluster
    node1[node1]
    node2[node2]
    node3[node3]
    redis[Redis]
  end
  node1 -- http --> node2
  node2 -- http --> node3
  node3 -- http --> node1
  node1 -- pub/sub --> redis
  node2 -- pub/sub --> redis
  node3 -- pub/sub --> redis



