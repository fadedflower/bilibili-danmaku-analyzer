#!/usr/bin/env python
# coding: utf-8

"""Serves UI pages and API"""

from os import path
from aiohttp import web
from .analyzer_api import ApiRoutes


class AnalyzerServer:
    """AnalyzerServer class.

    AnalyzerServer objects are the ones responsible for starting up analyzer server
    and serving api and ui pages.
    """
    ui_path = path.join('visualizer_ui', 'dist')

    def __init__(self):
        """Create a AnalyzerServer object"""
        if not path.exists(path.join(self.ui_path, 'index.html')):
            raise FileNotFoundError('"index.html" not found')
        self.app_server = web.Application()
        # 初始化路由
        self.app_server.router.add_routes(ApiRoutes)
        self.app_server.router.add_static('/ui/assets', path=path.join(self.ui_path, 'assets'))
        self.app_server.router.add_get('/ui/{path:.*}', self._index)

    @staticmethod
    async def _index(_request: web.Request):
        return web.FileResponse(path.join(AnalyzerServer.ui_path, 'index.html'))

    async def run(self, port: int = 8080):
        """Start up server and listen to the specified port"""
        runner = web.AppRunner(self.app_server)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
