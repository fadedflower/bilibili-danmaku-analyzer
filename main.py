#!/usr/bin/env python
# coding: utf-8

import asyncio
import bilibili_api as bapi
from danmaku_db import DanmakuDB


async def main() -> None:
    db = DanmakuDB()
    # credential = bapi.login.login_with_qrcode()
    await db.fetch_from_video('BV1j4411W7F7')
    db.to_wordcloud()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
