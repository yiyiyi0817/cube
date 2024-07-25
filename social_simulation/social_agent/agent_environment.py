from __future__ import annotations

import json
from abc import ABC, abstractmethod
from string import Template

from social_simulation.social_agent.community_agent_action import CommunityAction
from social_simulation.clock.clock import Clock
from datetime import datetime


class Environment(ABC):

    @abstractmethod
    def to_text_prompt(self) -> str:
        r"""Convert the environment to text prompt.
        """
        raise NotImplementedError


class SocialEnvironment(Environment):
    followers_env_template = Template("I have $num_followers followers.")
    follows_env_template = Template("I have $num_follows follows.")

    posts_env_template = Template(
        "After refreshing, you see some posts $posts")
    env_template = Template(
        "$posts_env\npick one you want to perform action that best "
        "reflects your current inclination based on your profile and "
        "posts content. Do not limit your action in just `like` to like posts")

    def __init__(self, action: SocialAction):
        self.action = action

    async def get_posts_env(self) -> str:
        posts = await self.action.refresh()
        # TODO: Replace posts json format string to other formats
        if posts["success"]:
            posts_env = json.dumps(posts["posts"], indent=4)
            posts_env = self.posts_env_template.substitute(posts=posts_env)
        else:
            posts_env = "After refreshing, there are no existing posts."
        return posts_env

    async def get_followers_env(self) -> str:
        # TODO: Implement followers env
        return self.followers_env_template.substitute(num_followers=0)

    async def get_follows_env(self) -> str:
        # TODO: Implement follows env
        return self.follows_env_template.substitute(num_follows=0)

    async def to_text_prompt(
        self,
        include_posts: bool = True,
        include_followers: bool = False,
        include_follows: bool = False,
    ) -> str:
        followers_env = await self.get_followers_env(
        ) if include_follows else "No followers."
        follows_env = await self.get_follows_env(
        ) if include_followers else "No follows."
        posts_env = await self.get_posts_env() if include_posts else ""

        return self.env_template.substitute(
            followers_env=followers_env,
            follows_env=follows_env,
            posts_env=posts_env,
        )


class CommunityEnvironment(Environment):
    current_time_template = Template("The current time is :$current_time\n")
    daily_plan_template = Template("Usually, your daily plan is $plan\n")

    current_room_template = Template(
        "You are at $room now.\n")
    env_template = Template(
        "$current_room $current_time $daily_plan pick one you want to "
        "perform action that best reflects your current inclination based on "
        "your profile, your current location, time, and daily schedule.")

    def __init__(
            self, clock: Clock, start_time: datetime,
            plan: str, action: CommunityAction):
        self.action = action
        self.room = None
        self.clock = clock
        self.start_time = start_time
        self.plan = plan

    async def get_room_env(self) -> str:
        room = self.room
        if room:
            room_env = self.current_room_template.substitute(room=room)
        else:
            room_env = "Now your location is unknown"
        return room_env

    async def get_time_env(self) -> str:
        current_time = self.clock.time_transfer(
            datetime.now(), self.start_time)
        return self.current_time_template.substitute(
            current_time=current_time)

    async def get_plan_env(self) -> str:
        # TODO: Implement follows env
        plan = self.plan
        return self.daily_plan_template.substitute(plan=plan)

    async def to_text_prompt(
        self,
    ) -> str:
        time_env = await self.get_time_env()
        plan_env = await self.get_plan_env()
        room_env = await self.get_room_env()

        return self.env_template.substitute(
            current_time=time_env,
            daily_plan=plan_env,
            current_room=room_env,
        )