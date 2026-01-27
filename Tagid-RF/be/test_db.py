import asyncio
from prisma import Prisma

async def test():
    p = Prisma()
    await p.connect()
    print('DB Connected!')
    await p.disconnect()

asyncio.run(test())
