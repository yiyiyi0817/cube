import asyncio
import os
import os.path as osp

import pytest

from cube.social_agent.agent import SocialAgent
from cube.social_agent.agents_generator import \
    generate_controllable_agents
from cube.social_platform.channel import Channel
from cube.social_platform.config import UserInfo
from cube.social_platform.platform import Platform

parent_folder = osp.dirname(osp.abspath(__file__))
test_db_filepath = osp.join(parent_folder, "test.db")


# 定义一个fixture来初始化数据库和Twitter实例
@pytest.fixture
def setup_twitter():
    # 测试前确保test.db不存在
    if os.path.exists(test_db_filepath):
        os.remove(test_db_filepath)


@pytest.mark.asyncio
async def test_perform_action_by_hci(monkeypatch, setup_twitter):
    channel = Channel()

    infra = Platform(test_db_filepath, channel, rec_update_time=1)
    task = asyncio.create_task(infra.running())

    inputs = iter(["Alice", "Ali", "a student"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    agent_graph, _ = await generate_controllable_agents(channel, 1)
    test_agent = agent_graph.get_agent(0)
    assert test_agent.user_info.is_controllable is True

    user_info = UserInfo(profile={'other_info': {'user_profile': 'None'}})
    operated_agent = SocialAgent(1, user_info, channel)
    await operated_agent.env.action.sign_up("user0101", "User", "A bio.")

    param_lst = [
        'hello world', '2', '2', '1', '1', '1', '1', 'hello', 'user', '0', '0',
        '1'
    ]

    for i in range(12):
        if param_lst[i] is not None:
            inputs = iter([i, param_lst[i]])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        else:
            inputs = iter([i])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        result = await test_agent.perform_action_by_hci()
        assert result['success'] is True

    await channel.write_to_receive_queue((None, None, "exit"))
    await task
