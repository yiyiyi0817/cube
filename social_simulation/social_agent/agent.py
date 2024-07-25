from __future__ import annotations

import inspect
import json
from typing import TYPE_CHECKING, Any
import logging
from datetime import datetime

from camel.configs import ChatGPTConfig, OpenSourceConfig
from camel.memories import (ChatHistoryMemory, MemoryRecord,
                            ScoreBasedContextCreator)
from camel.messages import BaseMessage
from camel.models import BaseModelBackend, ModelFactory
from camel.types import ModelType, OpenAIBackendRole
from camel.agents.chat_agent import ChatAgent
from colorama import Fore, Style

from social_simulation.social_agent.community_agent_action import CommunityAction
from social_simulation.social_agent.agent_environment import CommunityEnvironment
from social_simulation.social_platform import Channel
from social_simulation.social_platform.config import UserInfo
from social_simulation.clock.clock import Clock

if TYPE_CHECKING:
    from social_simulation.social_agent import AgentGraph


agent_log = logging.getLogger(name='social.agent')
agent_log.setLevel('DEBUG')
file_handler = logging.FileHandler('social.agent.log')
file_handler.setLevel('DEBUG')
file_handler.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s'))
agent_log.addHandler(file_handler)


class SocialAgent:

    def __init__(
        self,
        agent_id: int,
        user_info: UserInfo,
        channel: Channel,
        clock: Clock,
        start_time: datetime,
        model_path:
        str = "/mnt/hwfile/trustai/models/Meta-Llama-3-8B-Instruct",  # noqa
        server_url: str = "http://10.140.0.144:8000/v1",
        stop_tokens: list[str] = None,
        model_type: ModelType = ModelType.GPT_3_5_TURBO,
        temperature: float = 0.0,
        agent_graph: "AgentGraph" = None,
    ):
        self.agent_id = agent_id
        self.user_info = user_info
        self.channel = channel
        self.env = CommunityEnvironment(
            clock, start_time, None, CommunityAction(agent_id, channel))
        # print(self.user_info.to_community_system_message())
        self.system_message = BaseMessage.make_assistant_message(
            role_name="User",
            content=self.user_info.to_community_system_message(),
        )
        self.model_type = model_type

        if model_type.is_open_source:
            self.has_function_call = False
            api_params = ChatGPTConfig(
                temperature=temperature,
                stop=stop_tokens,
            )
            model_config = OpenSourceConfig(
                model_path=model_path,
                server_url=server_url,
                api_params=api_params,
            )
        else:
            self.has_function_call = True
            model_config = ChatGPTConfig(
                temperature=temperature,
                tools=self.env.action.get_openai_function_list(),
            )
        self.model_backend: BaseModelBackend = ModelFactory.create(
            model_type, model_config.__dict__)
        self.model_token_limit = self.model_backend.token_limit
        context_creator = ScoreBasedContextCreator(
            # self.model_backend.token_counter,
            self.model_token_limit,
        )
        self.memory = ChatHistoryMemory(context_creator, window_size=5)
        # self.system_message = BaseMessage.make_assistant_message(
        #     role_name="system",
        #     content=self.user_info.to_system_message()  # system prompt
        # )
        self.agent_graph = agent_graph
        print(Fore.GREEN + f"{agent_id}: model type {model_type}" + Fore.RESET)

    def plan_daily_life(self):
        plan_message = BaseMessage.make_user_message(
            role_name="User",
            content=(
                f"Use your role information: \n"
                f"{self.user_info.to_community_system_message()} \n"
                f"to briefly plan your daily schedule."
            )
        )
        plan_agent = ChatAgent(self.system_message)
        response = plan_agent.step(plan_message)
        self.schedule = response.msg.content
        self.env.plan = response.msg.content

    async def perform_action_by_llm(self):
        # Get 5 random tweets:
        env_prompt = await self.env.to_text_prompt()
        user_msg = BaseMessage.make_user_message(
            role_name="User",
            content=(
                f"Please perform social media actions after observing the "
                f"platform environments. Notice that don't limit your actions "
                f"for example to just like the posts. "
                f"Here is your social media environment: {env_prompt}"),
        )
        self.memory.write_record(
            MemoryRecord(
                user_msg,
                OpenAIBackendRole.USER,
            ))

        openai_messages, num_tokens = self.memory.get_context()
        content = ""

        # agent_log.info(f"Agent {self.agent_id} is running with prompt: {openai_messages}")

        if self.has_function_call:
            response = await self.model_backend.arun(openai_messages)
            # agent_log.info(f"Agent {self.agent_id} response: {response}")
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    action_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"Agent {self.agent_id} is performing "
                          f"twitter action: {action_name} with args: {args}")
                    await getattr(self.env.action, action_name)(**args)
                    self.perform_agent_graph_action(action_name, args)

        else:
            retry = 5
            exec_functions = []

            while retry > 0:
                start_message = openai_messages[0]
                if start_message["role"] != self.system_message.role_name:
                    openai_messages = [{
                        "role": self.system_message.role_name,
                        "content": self.system_message.content
                    }] + openai_messages

                response = self.model_backend.arun(openai_messages)
                agent_log.info(f"Agent {self.agent_id} response: {response}")
                content = response.choices[0].message.content
                try:
                    content_json = json.loads(content)
                    functions = content_json['functions']
                    reason = content_json['reason']
                    print(f"Agent {self.agent_id} choose "
                          f"{functions} \nbecause: {reason}.")
                    for function in functions:
                        name = function['name']
                        arguments = function['arguments']
                        print(f"Agent {self.agent_id} is performing "
                              f"twitter action: {name} with args: {arguments}")
                        exec_functions.append({
                            'name': name,
                            'arguments': arguments
                        })
                        self.perform_agent_graph_action(name, arguments)
                    break
                except Exception as e:
                    print(Fore.LIGHTRED_EX + f"Agent {self.agent_id}, time " +
                          Style.BRIGHT + str(retry) + Style.RESET_ALL +
                          f"\nError: {e} when parsing response:{content}\n" +
                          Fore.RESET + "=" * 20 + "\n")
                    print(Fore.LIGHTBLUE_EX + "For DEBUG, Messages:",
                          openai_messages, "\n" + Fore.RESET + "=" * 20 + "\n")
                    exec_functions = []
                    retry -= 1
            for function in exec_functions:
                try:
                    await getattr(self.env.action,
                                  function['name'])(**function['arguments'])
                except Exception as e:
                    print(Fore.LIGHTRED_EX + f"Agent {self.agent_id}, time " +
                          Style.BRIGHT + str(retry) + Style.RESET_ALL +
                          f"\nError: {e} when performing twitter action:" +
                          f" {function['name']} with " +
                          f"args: {function['arguments']}\n" + Fore.RESET +
                          "=" * 20 + "\n")

        agent_msg = BaseMessage.make_assistant_message(role_name="Assistant",
                                                       content=content)
        self.memory.write_record(
            MemoryRecord(agent_msg, OpenAIBackendRole.ASSISTANT))

    async def perform_action_by_hci(self) -> Any:
        print('Please choose one function to perform:')
        function_list = self.env.action.get_openai_function_list()
        for i in range(len(function_list)):
            print(f"{i}.", function_list[i].func.__name__, end=', ')
        print()

        selection = int(input("Enter your choice: "))
        if not 0 <= selection < len(function_list):
            print("Invalid input. Please enter a number.")
            return
        func = function_list[selection].func

        params = inspect.signature(func).parameters
        args = []
        for param in params.values():
            while True:
                try:
                    value = input(f"Enter value for {param.name}: ")
                    args.append(value)
                    break
                except ValueError:
                    print("Invalid input, please enter an integer.")

        result = await func(*args)
        return result

    async def perform_action_by_data(self, func_name, *args, **kwargs) -> Any:
        function_list = self.env.action.get_openai_function_list()
        for i in range(len(function_list)):
            if function_list[i].func.__name__ == func_name:
                func = function_list[i].func
                result = await func(*args, **kwargs)
                print(result)
                return result
        raise ValueError(f"Function {func_name} not found in the list.")

    def perform_agent_graph_action(
        self,
        action_name: str,
        arguments: dict[str, Any],
    ):
        r"""Remove edge if action is unfollow or add edge
        if action is follow to the agent graph.
        """
        if "unfollow" in action_name:
            followee_id: int | None = arguments.get("followee_id", None)
            if followee_id is None:
                return
            self.agent_graph.remove_edge(self.agent_id, followee_id)
            agent_log.info(f"Agent {self.agent_id} unfollowed {followee_id}")
        elif "follow" in action_name:
            followee_id: int | None = arguments.get("followee_id", None)
            if followee_id is None:
                return
            self.agent_graph.add_edge(self.agent_id, followee_id)
            agent_log.info(f"Agent {self.agent_id} followed {followee_id}")

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}(agent_id={self.agent_id}, "
                f"model_type={self.model_type.value})")
