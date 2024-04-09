from .base import BaseLLM

class NaiveLLM(BaseLLM):
    def __init__(self):
        pass

    def _call(self, history, *args, **kwargs):
        return history[-1]

    async def _acall(self, history, *args, **kwargs):
        return await self._call(history, *args, **kwargs)
    