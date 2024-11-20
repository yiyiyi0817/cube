import asyncio
import random
from cube.social_platform.unity_api.unity_server import (
    start_server, stop_server, send_position_to_unity,
    send_stop_to_unity
)
from cube.social_platform.unity_api.unity_queue_manager import UnityQueueManager

async def random_position():
    return random.uniform(-5, 5), 0, random.uniform(-5, 5)

async def main():
    # 启动服务器
    unity_queue_manager = UnityQueueManager(['Agent1', 'Agent2', 'Agent3'])
    server_tasks = await start_server(unity_queue_manager)

    try:
        # 等待服务器完全启动
        await asyncio.sleep(5)

        # 初始化 agents
        agents = ["Agent1", "Agent2", "Agent3"]
        for agent in agents:
            x, y, z = await random_position()
            await send_position_to_unity(agent, x, y, z)
            await asyncio.sleep(1)

        # 模拟随机控制和消息接收
        for _ in range(40):  # 执行40次循环
            await asyncio.sleep(random.uniform(0.5, 2))  # 随机等待0.5-2秒

            # 检查接收到的消息
            received_message = await unity_queue_manager.get_message('Agent2')
            while received_message:
                if received_message['message'].startswith("NEW_AGENT:"):
                    agent_name = received_message['agent_name']
                    new_agent = received_message['message'].split(":")[1]
                    print(f"New nearby agent detected for {agent_name}: {new_agent}")
                    await send_stop_to_unity(agent_name)
                    await asyncio.sleep(1)
                    x, y, z = await random_position()
                    await send_position_to_unity(agent_name, x, y, z)
                received_message = await unity_queue_manager.get_message('Agent2')

            # 随机发送命令
            if random.random() < 0.3:  # 30% 的概率发送命令
                agent = random.choice(agents)
                if random.choice([True, False]):
                    x, y, z = await random_position()
                    print(f"Sending new position to {agent}: ({x}, {y}, {z})")
                    await send_position_to_unity(agent, x, y, z)
                else:
                    print(f"Sending stop command to {agent}")
                    await send_stop_to_unity(agent)

    except KeyboardInterrupt:
        print("Stopping the control script...")
    finally:
        # 停止服务器
        await stop_server(*server_tasks)

if __name__ == "__main__":
    asyncio.run(main())