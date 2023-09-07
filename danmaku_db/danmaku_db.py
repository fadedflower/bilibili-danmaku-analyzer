#!/usr/bin/env python
# coding: utf-8

import asyncio
import math

import bilibili_api as bapi
import bilibili_api.utils.credential as bapi_credential
import pandas as pd
import danmaku_db.dm_pb2 as Danmaku
import requests
import json

class DanmakuDBError(Exception):
    pass


class DanmakuDB:
    """DanmakuDB class.

    DanmakuDB objects are the ones responsible of fetching video danmakus
    and exporting them to an Excel sheet.
    """
    def __init__(self):
        """Create a DanmakuDB object"""
        self.danmaku_list = {}

    def __len__(self):
        """Size of danmakus"""
        return len(self.danmaku_list)

    def __getitem__(self, item):
        """Get the danmaku at the specified index"""
        return self.danmaku_list[item]

    def __setitem__(self, key, value):
        """Set the danmaku at the specified index"""
        self.danmaku_list[key] = value

    async def fetch_from_video(self, bvid, credential=None):
        """Fetch danmakus from specific video and append them to danmaku_list"""
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
        self.danmaku_list[bvid] = danmaku_list

    def to_excel(self, filename):
        """Write danmakus to Excel sheets"""
        if len(self.danmaku_list) == 0:
            raise DanmakuDBError('Empty database')
        danmaku_dataframe = pd.DataFrame()
        for bvid, danmakus in self.danmaku_list.items():
            # 根据需要增加行数
            danmaku_dataframe = danmaku_dataframe.reindex(range(max(len(danmaku_dataframe), len(danmakus))))
            danmaku_dataframe[bvid] = danmakus

        danmaku_dataframe.to_excel(filename, sheet_name='danmakus', index=False)
        with pd.ExcelWriter(filename, mode='a', engine='openpyxl') as writer:
            danmaku_value_counts = pd.concat([danmaku_dataframe[col] for col in danmaku_dataframe.columns], ignore_index=True).value_counts()
            danmaku_value_counts.name = 'Counts'
            danmaku_value_counts.to_excel(writer, sheet_name='danmakus_count')

    def append(self, bvid, danmaku):
        """Append a danmaku to the database manually"""
        if bvid in self.danmaku_list.keys():
            self.danmaku_list[bvid].append(danmaku)
        else:
            self.danmaku_list[bvid] = [danmaku]

    def bvids(self):
        """Get the bvid list of the database"""
        return self.danmaku_list.keys()

    def clear(self):
        """Clear the danmaku database"""
        self.danmaku_list.clear()
