# -*- coding: utf-8 -*-
__author__ = 'ji_bu_de'
__time__ = '2019-08-29 21:24'
import asyncio

l = asyncio.Queue()
a = asyncio.Queue()

async def gogo():
    await asyncio.sleep(10)
    await l.put(1)

async def test():
    await gogo()
    print(await l.get())
    await l.put(1)
    a.put_nowait('as')
    print(await a.get())

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
if __name__ == '__main__':
    pass



