
class BaseLLM:
    def _call(self, history, *args, **kwargs):
        raise NotImplementedError

    async def _acall(self, history, *args, **kwargs):
        return await self._call(history, *args, **kwargs)