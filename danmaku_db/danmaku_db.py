#!/usr/bin/env python
# coding: utf-8

import bilibili_api as bapi
from bilibili_api.search import SearchObjectType
from bilibili_api.search import OrderVideo
import pandas as pd
import xml.etree.ElementTree as xmlReader
import io
import json
from wordcloud import WordCloud
import spacy_pkuseg as pkuseg
import string
from PIL import Image


class DanmakuDB:
    """DanmakuDB class.

    DanmakuDB objects are the ones responsible for fetching video danmakus
    and exporting them to an Excel sheet.
    """

    def __init__(self):
        """Create a DanmakuDB object"""
        self.danmaku_dict = {}

    def __len__(self) -> int:
        """Size of danmaku bvids"""
        return len(self.danmaku_dict)

    def __getitem__(self, bvid) -> list:
        """Get the danmaku list of the video of the specified bvid"""
        return self.danmaku_dict[bvid]

    def __setitem__(self, bvid: str, danmaku_list: list):
        """Set the danmaku list of the video of the specified bvid"""
        self.danmaku_dict[bvid] = danmaku_list

    async def fetch_from_video(self, bvid: str):
        """Fetch danmakus from specific video and add them to the database"""
        video = bapi.video.Video(bvid)
        danmaku_xml = await video.get_danmaku_xml(page_index=0)
        xml_tree = xmlReader.parse(io.StringIO(danmaku_xml))
        xml_root = xml_tree.getroot()
        danmaku_list = [d.text for d in xml_root.findall('./d')]
        for i in range(len(danmaku_list)):
            # 特殊处理高级弹幕，其内容为一个数组，弹幕实际内容在4号元素
            try:
                advanced_danmaku = json.loads(danmaku_list[i])
                if isinstance(advanced_danmaku, list):
                    danmaku_list[i] = advanced_danmaku[4]
            except json.decoder.JSONDecodeError:
                pass
        self.danmaku_dict[bvid] = danmaku_list

    async def fetch_from_search_result(self, keyword: str, max_n: int):
        """Fetch danmakus from videos in the search result and add them to the database"""
        num_results = None
        page = 1
        while len(self.danmaku_dict) < max_n and (num_results is None or len(self.danmaku_dict) < num_results):
            search_result = await bapi.search.search_by_type(keyword, SearchObjectType.VIDEO, OrderVideo.TOTALRANK,
                                                             page=page)
            num_results = search_result['numResults']
            # 计算该页应当获取的视频数
            fetch_count = (min(max_n, num_results, len(self.danmaku_dict) + len(search_result['result']))
                           - len(self.danmaku_dict))
            for i in range(fetch_count):
                await self.fetch_from_video(search_result['result'][i]['bvid'])
            page += 1

    def to_list(self) -> list:
        """Combine all the danmakus of the videos and create a list"""
        danmakus_list = []
        for v in self.danmaku_dict.values():
            danmakus_list += v
        return danmakus_list

    def to_excel(self, filename: str):
        """Write danmakus and related info to Excel sheets"""
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
        del danmaku_dataframe
        with pd.ExcelWriter(filename, mode='a', engine='openpyxl') as writer:
            danmaku_frequency = pd.Series(self.to_list()).value_counts()
            danmaku_frequency.name = 'Counts'
            danmaku_frequency.to_excel(writer, sheet_name='danmakus_frequency')

    def to_wordcloud(self, width: int, height: int, font_path: str = 'danmaku_db/fzht.ttf') -> Image:
        """Generate word cloud image based on danmakus"""
        if len(self.danmaku_dict) == 0:
            raise ValueError('Empty database')
        excluded_words = ['将', '\n', '地', '小说', '侧', '又', '一雄', '如何', '什么', '可以', '吗', '只是', '他',
                          '本', '们',
                          ' ',
                          '…', '把', '人', '很', '那么', '着', '太', '能', '给', '不是', '里', '被', '就是', '一个',
                          '没有',
                          '剧',
                          '让', '/', '而', '与', '一部', '的', '我', '你', '她', '我们', '你们', '他们', '是', '在',
                          '了', '有',
                          '这', '那', '就', '也', '还', '但', '如果', '然后', '因为', '所以', '一', '二', '三', '四',
                          '五',
                          '六',
                          '七', '八', '九', '十', '百', '千', '万', '个', '这些', '那些', '更', '最', '好', '坏', '大',
                          '小',
                          '高',
                          '低', '长', '短', '新', '旧', '常', '少', '多', '全', '每', '些', '去', '来', '到', '从',
                          '为', '以',
                          '对',
                          '和', '或', '及', '上', '下', '中', '前', '后', '左', '右', '内', '外', '间', '部', '种',
                          '年', '月',
                          '日',
                          '时', '分', '秒', '这里', '这个', '那个', '这样', '那样', '一些', '很多', '非常', '可能', '一定',
                          '一直',
                          '经常',
                          '不断', '不只', '不要', '不得', '不能', '无法', '没法', '必须', '应该', '需要', '会', '想',
                          '要',
                          '找',
                          '看', '听', '说', '写', '读', '学', '做', '吃', '喝', '睡', '玩', '工作', '生活', '家庭',
                          '朋友',
                          '嫌',
                          '之',
                          '感觉', '思考', '想法', '方法', '原因', '结果', '可能性', '比较', '不同', '相同', '重要',
                          '容易',
                          '困难',
                          '简单', '复杂', '正确', '错误', '，', '。', '！', '？', '；', '：', '“', '”', '‘', '’', '（', '）',
                          '【', '】',
                          '《',
                          '》', '——', '—', '·', '、', '～', '@', '?', '啊', '吧', '呢', '都', '过', '没', '得', '=', '~',
                          '追', '比', '呀', '跟', '啦', '哇', '不', '……', '…', '这不', '连', '懂', '真', '怎么',
                          '已经', '这么', '么', '超', '好像', '想到', '再', '变', '的话', '啊啊', '还是', '才', '为什么', '还有',
                          '别', '次', '事', '用', '条', '开', '两', '打', '哦', '只', '头', '哪', '男', '女', '段', '啥', '自',
                          '谁', '撅', '快', '最后', '等', '开', '它', '噗', '嗷', '噢', '哼', '唉', '啦', '嘞']
        excluded_words += list(string.punctuation + string.digits + string.ascii_letters)
        seg = pkuseg.pkuseg(model_name='web')
        word_frequency = pd.Series([[word for word in seg.cut(d) if word not in excluded_words]
                                    for d in self.to_list()]).explode(ignore_index=True).value_counts()
        wordcloud = WordCloud(font_path=font_path, background_color='white', width=width, height=height)\
            .generate_from_frequencies(word_frequency.to_dict())

        return wordcloud.to_image()

    def read_excel(self, filename: str):
        """Load danmakus from Excel sheets"""
        danmaku_dataframe = pd.read_excel(filename, sheet_name='danmakus')
        self.danmaku_dict = danmaku_dataframe.to_dict('list')
        # 滤去NAN
        for bvid in self.danmaku_dict.keys():
            self.danmaku_dict[bvid] = [danmaku for danmaku in self.danmaku_dict[bvid] if isinstance(danmaku, str)]

    def append(self, bvid: str, danmaku: str):
        """Append a danmaku to the database manually"""
        if bvid in self.danmaku_dict.keys():
            self.danmaku_dict[bvid].append(danmaku)
        else:
            self.danmaku_dict[bvid] = [danmaku]

    def bvids(self) -> list:
        """Get the bvid list of the database"""
        return list(self.danmaku_dict.keys())

    def items(self):
        """Get K-V view of the database"""
        return self.danmaku_dict.items()

    def clear(self):
        """Clear the danmaku database"""
        self.danmaku_dict.clear()
