import asyncio
from socialplatform.platform import Platform 

if __name__ == "__main__":
    platform = Platform()
    asyncio.run(platform.run())