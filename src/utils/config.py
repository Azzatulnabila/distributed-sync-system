# src/utils/config.py
import os

# node ids and ports (names used in docker-compose hostnames)
DEFAULT_NODES = ["node1", "node2", "node3"]

NODES = os.getenv("NODES", ",".join(DEFAULT_NODES)).split(",")
NODE_ID = os.getenv("NODE_ID", "node1")
PORT = int(os.getenv("PORT", "5000"))

# Redis config
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Raft-like timing
ELECTION_TIMEOUT = float(os.getenv("ELECTION_TIMEOUT", "6.0"))
HEARTBEAT_INTERVAL = float(os.getenv("HEARTBEAT_INTERVAL", "2.0"))

# Queue config
QUEUE_NAMESPACE = "ds_queue"
