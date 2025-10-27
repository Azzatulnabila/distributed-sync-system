# Deployment Guide - Docker Online (Play-with-Docker)

## Prasyarat
- Akun Docker Hub (untuk Play-with-Docker login)
- Repo GitHub: https://github.com/Azzatulnabila/distributed-sync-system

## Langkah cepat (Play-with-Docker)
1. Buka https://labs.play-with-docker.com/ → Login
2. Start new session → Add new instance (minimal 1)
3. Di terminal instance:
   ```bash
   git clone https://github.com/Azzatulnabila/distributed-sync-system.git
   cd distributed-sync-system/docker
   docker-compose up --build

## Jika docker-compose bermasalah di PWD, gunakan:
docker build -t ds-node -f Dockerfile.node ..
docker run -d --name redis redis:6-alpine
docker run -d --name node1 --env NODE_ID=node1 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node
docker run -d --name node2 --env NODE_ID=node2 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node
docker run -d --name node3 --env NODE_ID=node3 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node

## Cek logs:
docker ps
docker logs -f node1
docker logs -f node2

## Demo commands (dijalankan di container dengan akses network ke service):
curl -X POST http://node1:5000/lock/acquire -H "Content-Type: application/json" -d '{"resource":"r1","mode":"exclusive"}'
curl -X POST http://node2:5000/queue/produce -H "Content-Type: application/json" -d '{"topic":"t","message":"hello"}'
curl -X POST http://node3:5000/queue/consume -H "Content-Type: application/json" -d '{"topic":"t"}'
curl -X POST http://node2:5000/cache/write -H "Content-Type: application/json" -d '{"key":"k1","value":"v1"}'
