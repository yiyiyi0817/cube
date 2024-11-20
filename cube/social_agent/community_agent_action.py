from typing import Any

from camel.functions import OpenAIFunction

from cube.social_platform.channel import Channel
from cube.social_platform.typing import CommunityActionType, RoomName


class CommunityAction:

    def __init__(self, agent_id: int, channel: Channel):
        self.agent_id = agent_id
        self.channel = channel

    def get_openai_function_list(self) -> list[OpenAIFunction]:
        return [
            OpenAIFunction(func) for func in [
                self.go_to,
                self.do_something,
            ]
        ]

    async def perform_action(self, message: Any, type: str):
        message_id = await self.channel.write_to_receive_queue(
            (str(self.agent_id), message, type))
        response = await self.channel.read_from_send_queue(message_id)
        return response[2]

    async def go_to(self, room_name: RoomName):
        r"""Go to a specified room.

        This method invokes an asynchronous action to move the user or entity
        to a specified room based on the `room_name` argument. It simulates
        the action of going to a different room in a virtual environment. Upon
        successful execution, it returns a dictionary indicating success and
        the name of the room arrived at. Note that you can't go into other
        people's private rooms. And do not go to a room you already in now.

        Args:
            room_name (RoomName): The enum member representing the room to
                which the user or entity will go.

        Returns:
            dict: A dictionary with two key-value pairs. The 'success' key
                maps to a boolean indicating whether the action of going to
                the room was successful. The 'arrived' key maps to the string
                name of the room that was successfully reached.

            Example of a successful return:
            {"success": True, "arrived": "garden"}
        """
        return await self.perform_action(
            room_name, CommunityActionType.GO_TO.value)

    async def do_something(self, activity: str, duration: int):
        r"""Perform a specified activity for a set duration.

        Initiates an asynchronous action that simulates the user or entity
        performing a chosen activity for a specified amount of time in
        minutes. Activities can include eating, sleeping, working,
        drinking coffee, listening to music, having a conversation, etc.

        Args:
            activity (str): The activity to be performed (e.g., "eating",
                "sleeping", "working", "drinking coffee", "listening to
                music", "having a conversation").
            duration (int): The duration for which the activity is to be
                performed, in minutes.

        Returns:
            dict: A dictionary with two key-value pairs. The 'success' key
                maps to a boolean indicating whether the action of going to
                the room was successful. The 'activity' key maps to the string
                of the activity that was successfully done.

            Example of a successful return:
            {"success": True, "activity": "eat food"}
        """
        activity_message = (activity, duration)
        return await self.perform_action(
            activity_message, CommunityActionType.DO_SOMETHING.value)
