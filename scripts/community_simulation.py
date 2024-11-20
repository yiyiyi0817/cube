from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime

from colorama import Back
from yaml import safe_load
from colorama import Fore, Style
import sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from cube.clock.clock import Clock
from cube.social_agent.agents_generator import generate_community_agents
from cube.social_platform.channel import Channel
from cube.social_platform.platform import Platform
from cube.social_platform.typing import CommunityActionType
from cube.testing.show_db import print_db_contents
from cube.social_platform.unity_api.unity_queue_manager import UnityQueueManager
from cube.social_platform.unity_api.unity_server import start_server, stop_server


parser = argparse.ArgumentParser(description="Arguments for script.")
parser.add_argument(
    "--config_path",
    type=str,
    help="Path to the YAML config file.",
    required=False,
    default="",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "mock_community.db")
DEFAULT_USER_PATH = os.path.join(DATA_DIR, "community",
                                 "residents_info_7.json")

ROUND_POST_NUM = 20

# comminuty simulation逻辑:
# 1. generate all(10) agents, 根据mbti信息
# 2. 所有agents根据职业、年龄、性别等规划自己的时间表
# ------开始模拟，while 没到指定的结束时间------
# 3.1 refresh获取环境信息：当前时间、大计划表、现在的位置
# 3.2 perform action： walk_to/do_something
# (在结束之前listen to channel,如果相遇则send stop1-2秒后再次send pos)

# PS: 根据行动速度估算K=10
# platform的作用：记录trace/收发所有请求/维护社交图的关系
# db的重构：只保留trace table

# 分步计划：先按照时间步写，后面变成纯异步持续action

async def agent_task(agent):
    while True:
        await agent.perform_action_by_llm()
        await asyncio.sleep(0.1)  # 短暂休眠以允许其他任务运行

async def running(
    db_path: str | None = DEFAULT_DB_PATH,
    user_path: str | None = DEFAULT_USER_PATH,
    # num_timesteps: int = 3,
    clock_factor: int = 120,
) -> None:
    db_path = DEFAULT_DB_PATH if db_path is None else db_path
    user_path = DEFAULT_USER_PATH if user_path is None else user_path
    if os.path.exists(db_path):
        os.remove(db_path)
    # 实验从2024年7月1日早上八点开始
    start_time = datetime(2024, 7, 1, 8, 0)
    clock = Clock(k=clock_factor)
    channel = Channel()
    unity_queue_mgr = UnityQueueManager(['0', '1', '2', '3', '4', '5', '6'])
    infra = Platform(
        db_path,
        channel,
        unity_queue_mgr,
        clock,
        start_time,
    )
    await infra.create_async_db()
    task = asyncio.create_task(infra.running())

    agent_graph = await generate_community_agents(
        user_path,
        channel,
        clock,
        start_time
    )

    server_tasks = await start_server(unity_queue_mgr)
    print(Fore.GREEN + "please start unity in 10s...\n" + Fore.RESET)
    await asyncio.sleep(10)

    try:
        tasks = []
        for _, agent in agent_graph.get_agents():
            if agent.user_info.is_controllable is False:
                task = asyncio.create_task(agent_task(agent))
                tasks.append(task)

        await asyncio.gather(*tasks)
        '''
        for timestep in range(num_timesteps):
        print(Back.GREEN + f"timestep:{timestep}" + Back.RESET)
        tasks = []  # 初始化任务列表
        for _, agent in agent_graph.get_agents():
            if agent.user_info.is_controllable is False:
                # 将perform_action_by_llm的调用包装成一个任务，并添加到任务列表中
                task = asyncio.create_task(agent.perform_action_by_llm())
                tasks.append(task)
        # 异步等待所有任务完成
        await asyncio.gather(*tasks)'''

        await channel.write_to_receive_queue(
            (None, None, CommunityActionType.EXIT))
        await task
    except KeyboardInterrupt:
        print("Stopping the control script...")
    finally:
        # 停止服务器
        await stop_server(*server_tasks)

    print_db_contents(db_path)


if __name__ == "__main__":
    asyncio.run(running())
