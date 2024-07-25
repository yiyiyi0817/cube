from __future__ import annotations

import random
import sqlite3
import asyncio
from datetime import datetime
from typing import Any


from social_simulation.clock.clock import Clock
from social_simulation.social_platform.database import create_db
from social_simulation.social_platform.platform_utils import PlatformUtils
from social_simulation.social_platform.typing import CommunityActionType
from social_simulation.social_platform.unity_api.unity_server import (
    start_server, stop_server, send_position_to_unity,
    send_stop_to_unity, get_received_message
)
import logging

twitter_log = logging.getLogger(name='social.twitter')
twitter_log.setLevel('DEBUG')
file_handler = logging.FileHandler('social.twitter.log')
file_handler.setLevel('DEBUG')
file_handler.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s'))
twitter_log.addHandler(file_handler)

room_coordinate: dict = {
    "garden": (-17, 0, 14),
    "library": (19, 0, 14),
    "music room": (-23, 0, -13),
    "office": (-17, 0, -12),
    "school": (15, 0, -12)
}


# agent_action: 输入（room/do_something和持续时间），返回结束标志
# platform:输入agent_id, action_type, unity情况，返回到达/指定do_something时间结束
# 并在过程中记录agent指令和unity指令进入数据库
class Platform:
    async def __init__(
            self, db_path: str, channel: Any,
            sandbox_clock: Clock, start_time: datetime):
        create_db(db_path)
        server_tasks = await start_server()
        print("please start unity in 10s...")
        await asyncio.sleep(10)

        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db_cursor = self.db.cursor()

        self.channel = channel
        self.start_time = start_time
        self.sandbox_clock = sandbox_clock

        self.pl_utils = PlatformUtils(
            self.db, self.db_cursor, self.start_time, self.sandbox_clock)

    async def running(self):
        while True:
            message_id, data = await self.channel.receive_from()
            agent_id, message, action = data
            action = CommunityActionType(action)

            if action == CommunityActionType.EXIT:
                self.db_cursor.close()
                self.db.close()
                break
            elif action == CommunityActionType.GO_TO:
                pass
            elif action == CommunityActionType.STOP:
                pass
            elif action == CommunityActionType.DO_SOMETHING:
                pass
            else:
                raise ValueError(f"Action {action} is not supported")

    # 注册
    async def go_to(self, agent_id, room_name):
        current_time = self.sandbox_clock.time_transfer(
            datetime.now(), self.start_time)
        x, y, z = room_coordinate.get(room_name)
        await send_position_to_unity(agent_id, x, y, z)
        action_info = {"room": room_name}
        self.pl_utils._record_trace(agent_id, CommunityActionType.GO_TO.value,
                                    action_info, current_time)
        received_message = await get_received_message()
        while True:

        try:
            return {"success": True, "arrived_room": room_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def refresh(self, agent_id: int):
        try:
            user_id = self.pl_utils._check_agent_userid(agent_id)
            if not user_id:
                return self.pl_utils._not_signup_error_message(agent_id)

            # 从rec表中获取指定user_id的所有post_id
            rec_query = "SELECT post_id FROM rec WHERE user_id = ?"
            self.pl_utils._execute_db_command(rec_query, (user_id, ))
            rec_results = self.db_cursor.fetchall()

            post_ids = [row[0] for row in rec_results]
            selected_post_ids = post_ids

            # 如果post_id数量 >= self.refresh_post_count，则随机选择指定数量的post_id
            if len(post_ids) >= self.refresh_post_count:
                selected_post_ids = random.sample(post_ids,
                                                  self.refresh_post_count)

            # 根据选定的post_id从post表中获取post详情
            placeholders = ', '.join('?' for _ in selected_post_ids)
            # 构造SQL查询字符串
            post_query = (
                f"SELECT post_id, user_id, content, created_at, num_likes, "
                f"num_dislikes FROM post WHERE post_id IN ({placeholders})")
            self.pl_utils._execute_db_command(post_query, selected_post_ids)
            results = self.db_cursor.fetchall()
            if not results:
                return {"success": False, "message": "No posts found."}
            results_with_comments = self.pl_utils._add_comments_to_posts(
                results)
            # 记录操作到trace表
            action_info = {"posts": results_with_comments}
            self.pl_utils._record_trace(user_id, ActionType.REFRESH.value,
                                        action_info)

            return {"success": True, "posts": results_with_comments}
        except Exception as e:
            return {"success": False, "error": str(e)}