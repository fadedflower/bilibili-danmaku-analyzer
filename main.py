#!/usr/bin/env python
# coding: utf-8

import asyncio
from danmaku_db import DanmakuDB


async def main() -> None:
    db = DanmakuDB()
    await db.fetch_from_video('BV1j4411W7F7')
    await db.fetch_from_video('BV1yt4y1Q7SS')
    db.to_excel('test.xlsx')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
