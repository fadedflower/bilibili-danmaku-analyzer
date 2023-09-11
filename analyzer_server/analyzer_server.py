#!/usr/bin/env python
# coding: utf-8

from .analyzer_api import ApiRoutes
from aiohttp import web
import os.path as path


class AnalyzerServer:
    """AnalyzerServer class.

    AnalyzerServer objects are the ones responsible for starting up analyzer server and serving api and ui pages.
    """
    def __init__(self):
        """Create a AnalyzerServer object"""
        ui_path = path.join('visualizer_ui', 'dist')
        if not path.exists(path.join(ui_path, 'index.html')):
            raise FileNotFoundError('"index.html" not found')
        self.app_server = web.Application()
        # 初始化路由
        self.app_server.router.add_routes(ApiRoutes)
        self.app_server.router.add_static('/ui/', path=ui_path, name='ui')

    async def run(self, port: int = 8080):
        """Start up server and listen to the specified port"""
        runner = web.AppRunner(self.app_server)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
