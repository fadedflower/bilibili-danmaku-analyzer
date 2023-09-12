#!/usr/bin/env python
# coding: utf-8

import asyncio
from analyzer_server import AnalyzerServer


async def main():
    server = AnalyzerServer()
    await server.run()
    print('本地服务器已启动，请访问“http://localhost:8080/ui/main”以使用该工具。')
    print('按下“Ctrl+C”以停止服务器运行...')
    await asyncio.Event().wait()


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
