from __future__ import annotations

import random
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Any


from cube.clock.clock import Clock
from cube.social_platform.database import create_db_async
from cube.social_platform.platform_utils import AsyncPlatformUtils
from cube.social_platform.typing import CommunityActionType
from cube.social_platform.unity_api.unity_server import (
    send_position_to_unity, send_stop_to_unity
)
from cube.social_platform.unity_api.unity_queue_manager import UnityQueueManager

import logging

twitter_log = logging.getLogger(name='social.twitter')
twitter_log.setLevel('DEBUG')
file_handler = logging.FileHandler('social.twitter.log')
file_handler.setLevel('DEBUG')
file_handler.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s'))
twitter_log.addHandler(file_handler)

room_coordinate: dict = {
    "entrance(Building B)": (14, 0, 17),
    "kitchen(Building B)": (25, 0, 13),
    "dining room(Building B)": (0, 0, 14),

    "Bob's private toilet(Building B)": (0, 0, 20),
    "Bob's private living room(Building B)": (-1, 0, 23),
    "Bob's private bedroom(Building B)": (-1, 0, 26),
    "Bob's private balcony(Building B)": (-2, 0, 26),

    "entrance(Building A)": (-35, 0, 17),
    "kitchen(Building A)": (-46, 0, 13.3),
    "dining room(Building A)": (-22, 0, 14),

    "Alice's private toilet(Building A)": (-21, 0, 20),
    "Alice's private living room(Building A)": (-20, 0, 23),
    "Alice's private bedroom(Building A)": (-20, 0, 26),
    "Alice's private balcony(Building A)": (-18, 0, 26),

    "Daisy's private toilet(Building A)": (-27, 0, 20),
    "Daisy's private living room(Building A)": (-26, 0, 23),
    "Daisy's private bedroom(Building A)": (-26, 0, 26),
    "Daisy's private balcony(Building A)": (-24, 0, 26),

    "Lisa's private toilet(Building A)": (-33, 0, 20),
    "Lisa's private living room(Building A)": (-32, 0, 23),
    "Lisa's private bedroom(Building A)": (-32, 0, 26),
    "Lisa's private balcony(Building A)": (-30, 0, 26),

    "Tom's private toilet(Building A)": (-35, 0, 20),
    "Tom's private living room(Building A)": (-37, 0, 23),
    "Tom's private bedroom(Building A)": (-35, 0, 26),
    "Tom's private balcony(Building A)": (-38, 0, 26),

    "Andrew's private toilet(Building A)": (-40, 0, 20),
    "Andrew's private living room(Building A)": (-42, 0, 23),
    "Andrew's private bedroom(Building A)": (-40, 0, 26),
    "Andrew's private balcony(Building A)": (-43, 0, 26),

    "Amy's private toilet(Building A)": (-46, 0, 20),
    "Amy's private living room(Building A)": (-48, 0, 23),
    "Amy's private bedroom(Building A)": (-46, 0, 26),
    "Amy's private balcony(Building A)": (-49, 0, 26),

    "west garden": (12, 0, -5),
    "east garden": (-34, 0, -5),
    "square": (11, 0, -20),
    "basketball court": (-35, 0, -22),
    "card room": (-20, 0, -46),
    "north room in library": (-39, 0, -47),
    "south room in library": (-39, 0, -42),
    "activity room": (-48, 0, -46),

    "church": (13, 0, -34),

    "office": (-123, 0, -100),
    "school": (73, 0, -100)
}


# agent_action: 输入（room/do_something和持续时间），返回结束标志
# platform:输入agent_id, action_type, unity情况，返回到达/指定do_something时间结束
# 并在过程中记录agent指令和unity指令进入数据库
class Platform:
    def __init__(
            self, db_path: str, channel: Any,
            unity_queue_manager: UnityQueueManager,
            sandbox_clock: Clock, start_time: datetime):
        self.db_path = db_path
        self.channel = channel
        self.unity_queue_mgr = unity_queue_manager
        self.start_time = start_time
        self.sandbox_clock = sandbox_clock

        self.pl_utils = AsyncPlatformUtils(
            db_path, self.start_time, self.sandbox_clock)

    async def create_async_db(self):
        await create_db_async(self.db_path)
        # 其他可能的异步初始化代码
        self.pl_utils = AsyncPlatformUtils(
            self.db_path, self.start_time, self.sandbox_clock)
        return self

    async def running(self):
        tasks = []  # 用于跟踪所有创建的任务
        while True:
            message_id, data = await self.channel.receive_from()
            # print('platform receive:', message_id, data)
            if data[2] == CommunityActionType.EXIT:
                # 等待所有先前的任务完成
                if tasks:
                    await asyncio.gather(*tasks)
                break
            else:
                # 为每个消息创建一个新的任务，并跟踪它
                task = asyncio.create_task(self.handle_message(message_id, data))
                tasks.append(task)
                # 可选：清理已完成的任务，避免列表无限增长
                tasks = [t for t in tasks if not t.done()]

    async def handle_message(self, message_id, data):
        agent_id, message, action = data
        action = CommunityActionType(action)
        try:
            if action == CommunityActionType.EXIT:
                self.db_cursor.close()
                self.db.close()
                # 由于这里是退出操作，可能需要特殊处理以避免后续任务执行
            elif action == CommunityActionType.GO_TO:
                result = await self.go_to(agent_id=agent_id, room_name=message)
                print('goto_result:', result)
                await self.channel.send_to((message_id, agent_id, result))
            elif action == CommunityActionType.DO_SOMETHING:
                result = await self.do_something(
                    agent_id=agent_id, activity_message=message)
                print('do_something_result:', result)
                await self.channel.send_to((message_id, agent_id, result))
            else:
                raise ValueError(f"Action {action} is not supported")
        except Exception as e:
            # 处理或记录异常
            print(f"Error handling message {message_id}: {e}")

    async def go_to(self, agent_id: str, room_name: str):
        try:
            action_info = {"room": room_name}
            await self.pl_utils._record_trace(agent_id, "plan_to", action_info)
            x, y, z = room_coordinate.get(room_name)
            await send_position_to_unity(agent_id, x, y, z)

            listen_flag = True
            received_message = await self.unity_queue_mgr.get_message(agent_id)
            if received_message and received_message['message'].startswith("ARRIVED"):
                listen_flag = False

            # print('platform receive message:', received_message)
            while listen_flag:
                if received_message and received_message['message'].startswith("ARRIVED"):
                    await send_stop_to_unity(agent_id)
                    listen_flag = False
                if received_message and received_message['message'].startswith("NEW_AGENT:"):
                    new_agent = received_message['message'].split(":")[1]
                    # 记录相遇操作到trace表
                    action_info = {"new_agent": new_agent}
                    await self.pl_utils._record_trace(
                        agent_id, CommunityActionType.MEET.value, action_info)
                    await send_stop_to_unity(agent_id)
                    await asyncio.sleep(2)
                    await send_position_to_unity(agent_id, x, y, z)

                received_message = await self.unity_queue_mgr.get_message(
                    agent_id)

            # 记录go_to操作到trace表
            action_info = {"room": room_name}
            await self.pl_utils._record_trace(
                agent_id, "arrived", action_info)
            return {"success": True, "arrived": room_name}
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")
            print(f"Error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    async def do_something(
            self, agent_id: str, activity_message: tuple[str, int]):
        # duration单位是分钟
        try:
            start_time = self.sandbox_clock.time_transfer(
                datetime.now(), self.start_time)
            activity, duration = activity_message
            duration_delta: datetime = timedelta(minutes=duration)

            action_info = {"activity": activity}
            await self.pl_utils._record_trace(
                agent_id, "start_activity", action_info, start_time)

            while True:
                now_time = self.sandbox_clock.time_transfer(
                    datetime.now(), self.start_time)
                elapsed_time = now_time - start_time  # 计算已过去的时间
                # print('elapsed_time:', elapsed_time)
                if elapsed_time > duration_delta:
                    # print("Finished running for specified duration")
                    break

                received_message = await self.unity_queue_mgr.get_message(
                    agent_id)
                if received_message and received_message['message'].startswith("NEW_AGENT:"):
                    new_agent = received_message['message'].split(":")[1]
                    # 记录相遇操作到trace表
                    action_info = {"new_agent": new_agent}
                    await self.pl_utils._record_trace(
                        agent_id, CommunityActionType.MEET.value, action_info)

            # 记录go_to操作到trace表
            action_info = {"activity": activity}
            await self.pl_utils._record_trace(
                agent_id, "end_activity", action_info, now_time)
            return {"success": True, "activity": activity}
        except Exception as e:
            return {"success": False, "error": str(e)}
