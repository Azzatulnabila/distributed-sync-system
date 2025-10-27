import asyncio
import time
import random
from src.utils.config import NODES, NODE_ID, PORT, ELECTION_TIMEOUT, HEARTBEAT_INTERVAL
from src.communication.http_client import post

class RaftNode:
    def __init__(self, on_become_leader=None):
        self.node_id = NODE_ID
        self.peers = [n for n in NODES if n != NODE_ID]
        self.state = "follower"
        self.current_term = 0
        self.voted_for = None
        self.leader = None
        self.on_become_leader = on_become_leader
        self.last_heartbeat = time.time()

    async def start(self):
        asyncio.create_task(self._election_loop())
        asyncio.create_task(self._heartbeat_checker())

    async def _heartbeat_checker(self):
        while True:
            now = time.time()
            if self.state != "leader" and now - self.last_heartbeat > ELECTION_TIMEOUT:
                await self.start_election()
            await asyncio.sleep(0.5)

    async def _election_loop(self):
        while True:
            timeout = ELECTION_TIMEOUT + random.random()
            await asyncio.sleep(timeout)
            if self.state != "leader" and time.time() - self.last_heartbeat > timeout:
                await self.start_election()

    async def start_election(self):
        self.current_term += 1
        self.voted_for = self.node_id
        votes = 1
        for p in self.peers:
            host = p
            port = 5000
            try:
                r = await post(host, port, "/raft/request_vote", {"term": self.current_term, "candidate": self.node_id})
                if r.get("vote") is True:
                    votes += 1
            except:
                pass
        if votes > (len(NODES) // 2):
            self.state = "leader"
            self.leader = self.node_id
            if self.on_become_leader:
                await self.on_become_leader()
            asyncio.create_task(self._send_heartbeats())

    async def _send_heartbeats(self):
        while self.state == "leader":
            for p in self.peers:
                await post(p, 5000, "/raft/heartbeat", {"term": self.current_term, "leader": self.node_id})
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def handle_heartbeat(self, term, leader):
        self.last_heartbeat = time.time()
        if term >= self.current_term:
            self.current_term = term
            self.leader = leader
            self.state = "follower"
            return {"ok": True}
        return {"ok": False}

    async def handle_vote_request(self, term, candidate):
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
        if (self.voted_for is None or self.voted_for == candidate) and term >= self.current_term:
            self.voted_for = candidate
            return {"vote": True}
        return {"vote": False}
