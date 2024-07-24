from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime

from colorama import Back
from yaml import safe_load

from social_simulation.clock.clock import Clock
from social_simulation.social_agent.agents_generator import (
    gen_control_agents_with_data, generate_reddit_agents)
from social_simulation.social_platform.channel import Channel
from social_simulation.social_platform.platform import Platform
from social_simulation.social_platform.typing import ActionType
from social_simulation.testing.show_db import print_db_contents

parser = argparse.ArgumentParser(description="Arguments for script.")
parser.add_argument(
    "--config_path",
    type=str,
    help="Path to the YAML config file.",
    required=False,
    default="",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "mock_reddit.db")
DEFAULT_USER_PATH = os.path.join(DATA_DIR, "reddit",
                                 "filter_user_results.json")
DEFAULT_PAIR_PATH = os.path.join(DATA_DIR, "reddit", "RS-RC-pairs.json")

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

async def running(
    db_path: str | None = DEFAULT_DB_PATH,
    user_path: str | None = DEFAULT_USER_PATH,
    num_timesteps: int = 5,
    clock_factor: int = 60,
) -> None:
    db_path = DEFAULT_DB_PATH if db_path is None else db_path
    user_path = DEFAULT_USER_PATH if user_path is None else user_path
    if os.path.exists(db_path):
        os.remove(db_path)

    start_time = datetime.now()
    clock = Clock(k=clock_factor)
    channel = Channel()
    infra = Platform(
        db_path,
        channel,
        clock,
        start_time,
    )
    task = asyncio.create_task(infra.running())

    agent_graph = await generate_reddit_agents(
        user_path,
        channel,
        agent_graph,
        agent_user_id_mapping,
    )

    for timestep in range(num_timesteps):
        print(Back.GREEN + f"timestep:{timestep}" + Back.RESET)

        for _, agent in agent_graph.get_agents():
            # agent = node_data['agent']
            if agent.user_info.is_controllable is False:
                await agent.perform_action_by_llm()

    await channel.write_to_receive_queue((None, None, ActionType.EXIT))
    await task

    # print_db_contents(db_path)


if __name__ == "__main__":
    args = parser.parse_args()
    if os.path.exists(args.config_path):
        with open(args.config_path, "r") as f:
            cfg = safe_load(f)
        data_params = cfg.get("data")
        simulation_params = cfg.get("simulation")
        asyncio.run(running(**data_params, **simulation_params))
    else:
        asyncio.run(running())
