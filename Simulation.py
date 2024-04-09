import asyncio
from agentmanager.AgentManager import AgentManager
from threadmanager.ThreadManager import ThreadManager

async def main():
    agentmanager = AgentManager()
    agentmanager.creat(1000)
    threadmanager = ThreadManager(agentmanager)
    await asyncio.gather(threadmanager.RunAgent(), threadmanager.RunSocial())

if __name__ == "__main__":
    asyncio.run(main())