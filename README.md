# Distributed Sync System (Azzatul Nabila)

Proyek tugas Mata Kuliah: Sistem Paralel dan Terdistribusi  
Judul: Implementasi Distributed Synchronization System

## Ringkasan
Sistem simulasi terdistribusi dengan:
- Distributed Lock Manager (Raft-like + deadlock detector)
- Persistent Distributed Queue (Redis RPUSH + BLPOP)
- Cache Coherence (LRU + invalidation via Redis pub/sub)
- Containerized (Docker + docker-compose) — dirancang untuk diuji di Docker Online (Play-with-Docker)

## Struktur proyek
Lihat struktur di repo. (src/, docker/, tests/, docs/, benchmarks/)

## Cara menjalankan (Play-with-Docker / Docker Online)
1. Login ke https://labs.play-with-docker.com/
2. Start session → Add instance(s)
3. Di terminal:
   ```bash
   git clone https://github.com/Azzatulnabila/distributed-sync-system.git
   cd distributed-sync-system/docker
   docker-compose up --build

   Jika docker-compose tidak tersedia, jalankan manual:
   ```bash
   docker run -d --name redis redis:6-alpine
   docker build -t ds-node -f Dockerfile.node ..
   docker run -d --name node1 --env NODE_ID=node1 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node
   docker run -d --name node2 --env NODE_ID=node2 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node
   docker run -d --name node3 --env NODE_ID=node3 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node

4. Periksa status:
   ```bash
   docker ps
   docker logs -f node1

5. Contoh demo (di terminal yang bisa reach container hostnames):
   ```bash
   curl -X POST http://node1:5000/lock/acquire -H "Content-Type: application/json" -d '{"resource":"r1","mode":"exclusive"}'
   curl -X POST http://node2:5000/queue/produce -H "Content-Type: application/json" -d '{"topic":"t","message":"hello"}'
   curl -X POST http://node3:5000/queue/consume -H "Content-Type: application/json" -d '{"topic":"t"}'
   curl -X POST http://node2:5000/cache/write -H "Content-Type: application/json" -d '{"key":"k1","value":"v1"}'





