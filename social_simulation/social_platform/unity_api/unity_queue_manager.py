import asyncio
from typing import Dict, List


# 作用：1.生成所有队列， 2.存取所有消息
# agent的ID示例：1，2，3，4
class UnityQueueManager:
    def __init__(self, agent_ids: List[str]):
        self.queue_dict = {}
        for agent_id in agent_ids:
            self.queue_dict[agent_id] = asyncio.Queue()

    async def put_message(self, agent_id: str, message: dict):
        # print('put_message:', agent_id, message)
        await self.queue_dict[agent_id].put(message)

    async def get_message(self, agent_id: str, timeout: float = 15) -> dict:
        try:
            receive_result = await asyncio.wait_for(
                self.queue_dict[agent_id].get(), timeout=timeout)
            # print('\n\nget_received_message:', receive_result)
            return receive_result
        except asyncio.TimeoutError:
            return None
