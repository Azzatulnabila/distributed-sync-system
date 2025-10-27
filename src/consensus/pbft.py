"""
PBFT placeholder (optional bonus).
Implementasi lengkap PBFT cukup panjang; file ini berisi skeleton dan test hook
sehingga kamu bisa menambahkan demonstrasi sederhana jika ingin ambil bonus.
"""
import asyncio

class PBFTNode:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = nodes

    async def broadcast_preprepare(self, payload):
        for n in self.nodes:
            if n != self.node_id:
                pass
