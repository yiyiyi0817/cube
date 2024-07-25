import json
from datetime import datetime


class PlatformUtils:

    def __init__(self, db, db_cursor, start_time, sandbox_clock):
        self.db = db
        self.db_cursor = db_cursor
        self.start_time = start_time
        self.sandbox_clock = sandbox_clock

    @staticmethod
    def _not_signup_error_message(agent_id):
        return {
            "success":
            False,
            "error": (f"Agent {agent_id} have not signed up and have no "
                      f"user id.")
        }

    def _execute_db_command(self, command, args=(), commit=False):
        self.db_cursor.execute(command, args)
        if commit:
            self.db.commit()
        return self.db_cursor

    def _execute_many_db_command(self, command, args_list, commit=False):
        self.db_cursor.executemany(command, args_list)
        if commit:
            self.db.commit()
        return self.db_cursor

    def _record_trace(self,
                      user_id,
                      action_type,
                      action_info,
                      current_time=None):
        # 如果除了trace，该操作函数还在数据库的其他表中记录了时间，以进入操作函数的时间为准
        # 传入current_time，使得比如post table的created_at和trace表中时间一模一样

        # 如果只有trace表需要记录时间，将进入_record_trace作为trace记录的时间
        if current_time is None:
            current_time = self.sandbox_clock.time_transfer(
                datetime.now(), self.start_time)
        trace_insert_query = (
            "INSERT INTO trace (user_id, created_at, action, info) "
            "VALUES (?, ?, ?, ?)")
        action_info_str = json.dumps(action_info)
        self._execute_db_command(
            trace_insert_query,
            (user_id, current_time, action_type, action_info_str),
            commit=True)