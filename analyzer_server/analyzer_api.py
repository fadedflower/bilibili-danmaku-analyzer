#!/usr/bin/env python
# coding: utf-8
import math
from functools import wraps
from danmaku_db import DanmakuDB
from aiohttp import web
from bilibili_api import ApiException
import io

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


class ApiHelper:
    """ApiHelper class.

        ApiHelper provides methods to construct responses"""
    error_codes = [
        'success',
        'empty database',
        'bvid does not exist',
        'invalid page number',
        'invalid n number'
    ]

    @classmethod
    def response(cls, code: int = 0, data=None):
        """Construct JSON response"""
        if code < 0 or code >= len(cls.error_codes):
            raise ValueError('Error code out of bounds')
        if data is None:
            data = {}
        json_data = {
            'code': code,
            'message': cls.error_codes[code],
            **data
        }
        if code == 0:
            return web.json_response(json_data)
        else:
            return web.json_response(json_data, status=403)


class ApiHandler:
    """ApiHandler class.

    ApiHandler contains API request handlers"""
    db = DanmakuDB()

    @staticmethod
    @ApiRoutes.get('/api/fetch')
    @validate_param({'keyword': str, 'n': int})
    async def fetch(request: web.Request, **params):
        """Request handler for fetching videos' danmakus from search results"""
        ApiHandler.db.clear()
        await ApiHandler.db.fetch_from_search_result(params['keyword'], params['n'])
        return ApiHelper.response()

    @staticmethod
    @ApiRoutes.get('/api/wordcloud')
    @validate_param({'width': int, 'height': int})
    async def wordcloud(request: web.Request, **params):
        """Request handler for generating word cloud image"""
        if len(ApiHandler.db) == 0:
            return ApiHelper.response(1)
        image = ApiHandler.db.to_wordcloud(params['width'], params['height'])
        image_buf = io.BytesIO()
        image.save(image_buf, 'png')
        image_buf.seek(0)
        return web.Response(body=image_buf.read(), content_type="image/png")

    @staticmethod
    @ApiRoutes.get('/api/top_danmakus')
    @validate_param({'n': int})
    async def top_danmakus(request: web.Request, **params):
        """Request handler for getting top danmakus"""
        if params['n'] <= 0:
            return ApiHelper.response(4)
        if len(ApiHandler.db) == 0:
            return ApiHelper.response(1)
        data = {
            'top_danmakus': [{
                'danmaku': danmaku,
                'count': count
            } for danmaku, count in ApiHandler.db.top_danmakus(params['n'])]
        }
        return ApiHelper.response(data=data)

    @staticmethod
    @ApiRoutes.get('/api/export_excel')
    @validate_param({'filename': str})
    async def export_excel(request: web.Request, **params):
        """Request handler for exporting excel sheets"""
        if len(ApiHandler.db) == 0:
            return ApiHelper.response(1)
        ApiHandler.db.to_excel(params['filename'])
        return ApiHelper.response()

    @staticmethod
    @ApiRoutes.get('/api/db_info')
    async def db_info(request: web.Request):
        """Request handler for getting database info"""
        data = {
            'total_video_count': len(ApiHandler.db),
            'video_bvids': ApiHandler.db.bvids(),
            'video_danmaku_count': {bvid: len(ApiHandler.db[bvid]) for bvid in ApiHandler.db.bvids()},
            'total_danmaku_count': sum([len(ApiHandler.db[bvid]) for bvid in ApiHandler.db.bvids()])
        }
        return ApiHelper.response(data=data)

    @staticmethod
    @ApiRoutes.get('/api/db_data')
    @validate_param({'bvid': str, 'size': int, 'page': int})
    async def db_data(request: web.Request, **param):
        """Request handler for getting database info"""
        if param['bvid'] not in ApiHandler.db.bvids():
            return ApiHelper.response(2)
        if param['page'] <= 0:
            return ApiHelper.response(3)
        danmaku_count = len(ApiHandler.db[param['bvid']])
        # 参数标准化
        size = min(danmaku_count if param['size'] <= 0 else param['size'], danmaku_count)
        page_count = math.ceil(danmaku_count / size)
        page = min(param['page'], page_count)
        data = {
            'data': ApiHandler.db[param['bvid']][((page - 1) * size):page * size],
            'page_size': size,
            'page_count': page_count,
            'total_count': danmaku_count
        }
        data['page_size'] = len(data['data'])
        return ApiHelper.response(data=data)
