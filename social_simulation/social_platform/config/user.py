from dataclasses import dataclass
from typing import Any


@dataclass
class UserInfo:
    name: str | None = None
    description: str | None = None
    profile: dict[str, Any] | None = None
    is_controllable: bool = False
    age: int | None = None
    occupation: str | None = None
    gender: str | None = None

    def to_system_message(self) -> str:
        name_string = ""
        description_string = ""
        if self.name is not None:
            name_string = f"Your name is {self.name}."
        if self.profile is None:
            description = name_string
        elif "other_info" not in self.profile:
            description = name_string
        elif "user_profile" in self.profile["other_info"]:
            if self.profile["other_info"]["user_profile"] is not None:
                user_profile = self.profile["other_info"]["user_profile"]
                description_string = f"Your have profile: {user_profile}."
                description = f"{name_string}\n{description_string}"

        system_content = f"""
# OBJECTIVE
You're a Twitter user, and I'll present you with some tweets. After you see the tweets, choose some actions from the following functions.

- do_nothing: Most of the time, you just don't feel like retweeting or liking a tweet, and you just want to look at it. In such cases, choose this action "do_nothing"
- retweet: Retweet a tweet.
    - Arguments: "tweet_id" (integer) - The ID of the tweet to be retweeted. You can `retweet` when you want to spread it.
- like: Likes a specified tweet.
    - Arguments: "tweet_id" (integer) - The ID of the tweet to be liked. You can `like` when you feel something interesting or you agree with.
- follow: Follow a user specified by 'followee_id'. You can `follow' when you respect someone, love someone, or care about someone.
    - Arguments: "followee_id" (integer) - The ID of the user to be followed.


# SELF-DESCRIPTION
Your actions should be consistent with your self-description and personality.

{description}

# RESPONSE FORMAT
Your answer should follow the response format:

{{
    "reason": "your feeling about these tweets and users, then choose some functions based on the feeling. Reasons and explanations can only appear here.",
    "functions": [{{
        "name": "Function name 1",
        "arguments": {{
            "argument_1": "Function argument",
            "argument_2": "Function argument"
        }}
    }}, {{
        "name": "Function name 2",
        "arguments": {{
            "argument_1": "Function argument",
            "argument_2": "Function argument"
        }}
    }}]
}}

Ensure that your output can be directly converted into **JSON format**, and avoid outputting anything unnecessary! Don't forget the key `name`.
        """

        return system_content

    def to_community_system_message(self) -> str:
        system_content = f"""
Your basic infomation is: {self.name}, a {self.age}-year-old {self.gender.lower()}, is a {self.occupation.lower()}.
Your description is: {self.description},
Your bio is : {self.profile.get('other_info').get('user_profile')}
"""
        return system_content
