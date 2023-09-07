#!/usr/bin/env python
# coding: utf-8

import asyncio
import bilibili_api as bapi
import xml.etree.ElementTree as xmlReader
import io
import pandas as pd


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

    async def fetch_from_video(self, bvid):
        """Fetch danmakus from specific video and append them to danmaku_list"""
        video = bapi.video.Video(bvid)
        danmaku_xml = await video.get_danmaku_xml(page_index=0)
        xml_tree = xmlReader.parse(io.StringIO(danmaku_xml))
        xml_root = xml_tree.getroot()
        danmaku_list = [d.text for d in xml_root.findall('./d')]
        self.danmaku_list[bvid] = danmaku_list

    def to_excel(self, filename):
        """Write danmakus to Excel sheets"""
        if len(self.danmaku_list) == 0:
            raise DanmakuDBError('Empty database')
        danmaku_dataframe = pd.DataFrame(self.danmaku_list)
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
