#!/usr/bin/env python
# coding: utf-8

from functools import wraps
from danmaku_db import DanmakuDB
from aiohttp import web
from bilibili_api import ApiException

ApiRoutes = web.RouteTableDef()


def validate_param(param_dict: dict):
    """Validate request's parameter and append them to **params before proceeding"""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request: web.Request):
            params = {}
            for p, t in param_dict.items():
                if p not in request.query or request.query[p] == '':
                    return web.Response(status=400, text="Bad request")
                if t == bool and not request.query[p].lower() == 'true' and not request.query[p].lower() == 'false':
                    return web.Response(status=400, text="Bad request")
                try:
                    params[p] = t(request.query[p])
                except ValueError:
                    return web.Response(status=400, text="Bad request")
            try:
                return await handler(request, **params)
            except ApiException as e:
                return web.Response(status=500, text=e.msg)
        return wrapper
    return decorator


class ApiHandler:
    """ApiHandler class.

    ApiHandler contains API request handlers"""
    db = DanmakuDB()

    @staticmethod
    @ApiRoutes.get('/api/fetch')
    @validate_param({'keyword': str, 'n': int})
    async def fetch(request: web.Request, **params):
        """Request handler for fetching videos' danmakus from search results"""
        await ApiHandler.db.fetch_from_search_result(params['keyword'], params['n'])
        data = {
            'code': 0,
            'message': 'success'
        }
        return web.json_response(data)

    @staticmethod
    @ApiRoutes.get('/api/wordcloud')
    async def wordcloud(request: web.Request):
        """Request handler for generating word cloud image"""
        return web.Response(status=501, text='Method not implemented')

    @staticmethod
    @ApiRoutes.get('/api/top_danmakus')
    @validate_param({'n': int})
    async def top_danmakus(request: web.Request, **params):
        """Request handler for getting top danmakus"""
        return web.Response(status=501, text='Method not implemented')

    @staticmethod
    @ApiRoutes.get('/api/export_excel')
    @validate_param({'filename': str})
    async def export_excel(request: web.Request, **params):
        return web.Response(status=501, text='Method not implemented')
