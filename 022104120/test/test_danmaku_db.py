#!/usr/bin/env python
# coding: utf-8

"""Test module for danmaku_db"""

import os
import pytest
from danmaku_db import DanmakuDB

TEST_VALID_BVID1 = 'BV1j4411W7F7'
TEST_VALID_BVID2 = 'BV1yt4y1Q7SS'
TEST_MISSING_BVID = 'BV1gt411z78v'
TEST_INVALID_BVID = 'BV1'
TEST_EXCEL_FILENAME = 'test_danmakus.xlsx'
TEST_EXCEL_READ_FILENAME = 'test/excel_db.xlsx'
TEST_WORDCLOUD_FILENAME = 'test/wordcloud.png'
TEST_KEYWORD = '让子弹飞'


class TestDanmakuDB:
    """TestDanmakuDB class.

    Test class for danmaku_db
    """
    @pytest.fixture
    def danmaku_db(self):
        """Fixture, returns DanmakuDB"""
        return DanmakuDB()

    def test_append(self, danmaku_db):
        """Test append function"""
        danmaku_db.append(TEST_VALID_BVID1, 'Testing danmaku1')
        danmaku_db.append(TEST_VALID_BVID1, 'Testing danmaku2')
        assert len(danmaku_db) == 1 and TEST_VALID_BVID1 in danmaku_db.bvids()
        assert ('Testing danmaku1' in danmaku_db[TEST_VALID_BVID1]
                and 'Testing danmaku2' in danmaku_db[TEST_VALID_BVID1])

    def test_clear(self, danmaku_db):
        """Test clear function"""
        danmaku_db.append(TEST_VALID_BVID1, 'Testing danmaku')
        assert TEST_VALID_BVID1 in danmaku_db.bvids()
        assert len(danmaku_db) == 1 and 'Testing danmaku' in danmaku_db[TEST_VALID_BVID1]
        danmaku_db.clear()
        assert len(danmaku_db) == 0

    @pytest.mark.asyncio
    async def test_fetch_valid(self, danmaku_db):
        """Test fetch_from_video function"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        await danmaku_db.fetch_from_video(TEST_VALID_BVID2)
        assert TEST_VALID_BVID1 in danmaku_db.bvids() and TEST_VALID_BVID2 in danmaku_db.bvids()
        assert len(danmaku_db[TEST_VALID_BVID1]) > 10 and len(danmaku_db[TEST_VALID_BVID2]) > 10

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_fetch_missing(self, danmaku_db):
        """Test invalid fetch_from_video function call"""
        await danmaku_db.fetch_from_video(TEST_MISSING_BVID)

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_fetch_invalid(self, danmaku_db):
        """Test invalid fetch_from_video function call"""
        await danmaku_db.fetch_from_video(TEST_INVALID_BVID)

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_fetch_empty(self, danmaku_db):
        """Test invalid fetch_from_video function call"""
        await danmaku_db.fetch_from_video('')

    @pytest.mark.asyncio
    async def test_fetch_search(self, danmaku_db):
        """Test fetch_from_search_result function"""
        await danmaku_db.fetch_from_search_result(TEST_KEYWORD, 30)
        assert len(danmaku_db) == 30 and len(danmaku_db[danmaku_db.bvids()[0]]) > 10

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_fetch_search_empty(self, danmaku_db):
        """Test invalid fetch_from_search_result function call"""
        await danmaku_db.fetch_from_search_result('', -1)

    @pytest.mark.asyncio
    async def test_to_list(self, danmaku_db):
        """Test to_list function"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        assert len(danmaku_db.to_list()) > 10

    @pytest.mark.asyncio
    async def test_top_danmakus(self, danmaku_db):
        """Test test_top_danmakus function"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        assert len(danmaku_db.top_danmakus(10)) == 10

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_top_danmakus_invalid_n(self, danmaku_db):
        """Test invalid test_top_danmakus function call"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        danmaku_db.top_danmakus(0)

    def test_top_danmakus_empty(self, danmaku_db):
        """Test test_top_danmakus function call with empty database"""
        assert danmaku_db.top_danmakus(10) == {}

    @pytest.mark.asyncio
    async def test_to_excel_full(self, danmaku_db):
        """Test to_excel function call"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        danmaku_db.to_excel(TEST_EXCEL_FILENAME)
        assert os.path.exists(TEST_EXCEL_FILENAME)
        os.unlink(TEST_EXCEL_FILENAME)

    @pytest.mark.xfail
    def test_to_excel_empty_db(self, danmaku_db):
        """Test invalid to_excel function call"""
        danmaku_db.to_excel(TEST_EXCEL_FILENAME)
        assert os.path.exists(TEST_EXCEL_FILENAME)
        os.unlink(TEST_EXCEL_FILENAME)

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_to_excel_empty_filename(self, danmaku_db):
        """Test invalid to_excel function call"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        danmaku_db.to_excel('')

    def test_read_excel(self, danmaku_db):
        """Test read_excel function call"""
        danmaku_db.read_excel(TEST_EXCEL_READ_FILENAME)
        assert len(danmaku_db) == 3 and len(danmaku_db[danmaku_db.bvids()[0]]) > 10

    @pytest.mark.asyncio
    async def test_to_wordcloud(self, danmaku_db):
        """Test to_wordcloud function"""
        await danmaku_db.fetch_from_video(TEST_VALID_BVID1)
        danmaku_db.to_wordcloud().save(TEST_WORDCLOUD_FILENAME)
        assert os.path.exists(TEST_WORDCLOUD_FILENAME)
        os.unlink(TEST_WORDCLOUD_FILENAME)
