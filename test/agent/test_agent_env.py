from datetime import datetime
from cube.clock.clock import Clock
from cube.social_agent.agent_environment import CommunityEnvironment
import pytest


@pytest.mark.asyncio
async def test_comminity_env():
    plan = f'''
As TheOrganizer, CEO:
- Start the day with reviewing key business metrics and setting priorities for the day.
- Attend meetings with department heads to discuss strategies and address any issues.
- Allocate time for researching health trends and innovative education approaches.
- Engage in networking opportunities to exchange ideas and build connections.
- Dedicate time for personal development and reflection on applying traditional values in work and personal life.
- End the day by reflecting on achievements and planning for the next day's tasks.
- Stay connected with the team and community to make a positive impact through shared insights and experiences.
'''
    clock = Clock(60)
    start_time = datetime.now()
    com_env = CommunityEnvironment(clock, start_time, plan)
    com_env.room = 'Your bedroom'
    print(await com_env.to_text_prompt())
