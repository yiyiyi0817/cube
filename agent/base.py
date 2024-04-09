
class PersonalInfo:
    name: str

class Relationship:
    status: str
    partner: str

class BaseAgent:
    id: int

    def __init__(self, llm=None, personal_info=None):
        self.llm = llm
        self.personal_info = personal_info
        self.relationship = Relationship()

    async def _arun(self, history):
        return await self.llm._acall(history)