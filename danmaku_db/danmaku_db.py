#!/usr/bin/env python
# coding: utf-8

import asyncio
import math

import bilibili_api as bapi
from bilibili_api.search import SearchObjectType
from bilibili_api.search import OrderVideo
import bilibili_api.utils.credential as bapi_credential
import pandas as pd
import danmaku_db.dm_pb2 as Danmaku
import requests
import json


class DanmakuDB:
    """DanmakuDB class.

    DanmakuDB objects are the ones responsible of fetching video danmakus
    and exporting them to an Excel sheet.
    """
    def __init__(self):
        """Create a DanmakuDB object"""
        self.danmaku_dict = {}

    def __len__(self):
        """Size of danmaku bvids"""
        return len(self.danmaku_dict)

    def __getitem__(self, item):
        """Get the danmaku at the specified index"""
        return self.danmaku_dict[item]

    def __setitem__(self, key, value):
        """Set the danmaku at the specified index"""
        self.danmaku_dict[key] = value

    async def fetch_from_video(self, bvid, credential=None):
        """Fetch danmakus from specific video and add them to the database"""
        def fetch_danmaku_segment(cid, segment_index):
            api_url = 'https://api.bilibili.com/x/v2/dm/web/seg.so'
            # segment_index: 从1开始，每个片段代表一个6分钟的视频片段下的弹幕数据
            params = {
                'type': 1,
                'oid': cid,
                'segment_index': segment_index
            }
            resp = None
            # 登录后获取的弹幕内容更完整
            if credential is None:
                resp = requests.get(api_url, params)
            elif isinstance(credential, bapi_credential.Credential):
                resp = requests.get(api_url, params, cookies=credential.get_cookies())
            else:
                raise TypeError('Provided credential is of incorrect type')

            data = resp.content
            # 调用编译的Protobuf类对弹幕数据反序列化
            danmaku_seg = Danmaku.DmSegMobileReply()
            danmaku_seg.ParseFromString(data)
            # 获取弹幕内容
            danmaku_array = []
            for elem in danmaku_seg.elems:
                # 特殊处理高级弹幕，其内容为一个数组，弹幕实际内容在4号元素
                try:
                    advanced_danmaku = json.loads(elem.content)
                    if isinstance(advanced_danmaku, list):
                        danmaku_array.append(advanced_danmaku[4])
                    else:
                        danmaku_array.append(elem.content)
                except json.decoder.JSONDecodeError:
                    danmaku_array.append(elem.content)
            return danmaku_array

        video = bapi.video.Video(bvid)
        cid = await video.get_cid(0)
        info = await video.get_info()
        segments = math.ceil(info['duration'] / (60 * 6))
        danmaku_list = []
        for seg in range(1, segments + 1):
            danmaku_list += fetch_danmaku_segment(cid, seg)
        self.danmaku_dict[bvid] = danmaku_list

    async def fetch_from_search_result(self, keyword, max_n, credential=None):
        """Fetch danmakus from videos in the search result and add them to the database"""
        total_count = 0
        num_results = None
        page = 1
        while total_count < max_n and (num_results is None or total_count < num_results):
            search_result = await bapi.search.search_by_type(keyword, SearchObjectType.VIDEO, OrderVideo.TOTALRANK
                                                             , page=page)
            num_results = search_result['numResults']
            # 计算该页应当获取的视频数
            fetch_count = min(max_n, num_results, total_count + len(search_result['result'])) - total_count
            # 尝试以3个视频为一组进行并发执行
            fetch_group_count = 3
            for grp in range(0, fetch_count, fetch_group_count):
                fetch_tasks = [
                    asyncio.create_task(self.fetch_from_video(search_result['result'][i]['bvid'], credential))
                    for i in range(grp, min(grp + fetch_group_count, fetch_count))]
                for task in fetch_tasks:
                    await task
            total_count += fetch_count
            page += 1

    def to_excel(self, filename):
        """Write danmakus to Excel sheets"""
        if len(self.danmaku_dict) == 0:
            raise ValueError('Empty database')
        danmaku_dataframe = pd.DataFrame()
        for bvid, danmakus in self.danmaku_dict.items():
            # 根据需要增加行数
            danmaku_dataframe = danmaku_dataframe.reindex(range(max(len(danmaku_dataframe), len(danmakus))))
            if danmaku_dataframe.empty:
                danmaku_dataframe[bvid] = danmakus
            else:
                video_danmaku_dataframe = pd.DataFrame({bvid: danmakus})
                danmaku_dataframe = pd.concat([danmaku_dataframe, video_danmaku_dataframe], axis=1)

        danmaku_dataframe.to_excel(filename, sheet_name='danmakus', index=False)
        with pd.ExcelWriter(filename, mode='a', engine='openpyxl') as writer:
            danmaku_value_counts = pd.concat([danmaku_dataframe[col] for col in danmaku_dataframe.columns], ignore_index=True).value_counts()
            danmaku_value_counts.name = 'Counts'
            danmaku_value_counts.to_excel(writer, sheet_name='danmakus_count')

    def read_excel(self, filename):
        """Load danmakus from Excel sheets"""
        danmaku_dataframe = pd.read_excel(filename, sheet_name='danmakus')
        self.danmaku_dict = danmaku_dataframe.to_dict('list')
        # 滤去NAN
        for bvid in self.danmaku_dict.keys():
            self.danmaku_dict[bvid] = list(filter(lambda d: isinstance(d, str), self.danmaku_dict[bvid]))

    def append(self, bvid, danmaku):
        """Append a danmaku to the database manually"""
        if bvid in self.danmaku_dict.keys():
            self.danmaku_dict[bvid].append(danmaku)
        else:
            self.danmaku_dict[bvid] = [danmaku]

    def bvids(self):
        """Get the bvid list of the database"""
        return list(self.danmaku_dict.keys())

    def items(self):
        """Get K-V view of the database"""
        return self.danmaku_dict.items()

    def clear(self):
        """Clear the danmaku database"""
        self.danmaku_dict.clear()
