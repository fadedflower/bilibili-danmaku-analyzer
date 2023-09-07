#!/usr/bin/env python
# coding: utf-8

import pytest
import os
from danmaku_db import DanmakuDB

TEST_VALID_BVID1 = 'BV1j4411W7F7'
TEST_VALID_BVID2 = 'BV1yt4y1Q7SS'
TEST_MISSING_BVID = 'BV1gt411z78v'
TEST_INVALID_BVID = 'BV1'
TEST_EXCEL_FILENAME = 'test_danmakus.xlsx'


class TestDanmakuDB:

    @pytest.fixture
    def db(self):
        return DanmakuDB()

    def test_append(self, db):
        db.append(TEST_VALID_BVID1, 'Testing danmaku1')
        db.append(TEST_VALID_BVID1, 'Testing danmaku2')
        assert len(db) == 1 and TEST_VALID_BVID1 in db.bvids()
        assert 'Testing danmaku1' in db[TEST_VALID_BVID1] and 'Testing danmaku2' in db[TEST_VALID_BVID1]

    def test_clear(self, db):
        db.append(TEST_VALID_BVID1, 'Testing danmaku')
        assert TEST_VALID_BVID1 in db.bvids()
        assert len(db) == 1 and 'Testing danmaku' in db[TEST_VALID_BVID1]
        db.clear()
        assert len(db) == 0

    @pytest.mark.asyncio
    async def test_fetch_valid(self, db):
        await db.fetch_from_video(TEST_VALID_BVID1)
        await db.fetch_from_video(TEST_VALID_BVID2)
        assert TEST_VALID_BVID1 in db.bvids() and TEST_VALID_BVID2 in db.bvids()
        assert len(db[TEST_VALID_BVID1]) > 10 and len(db[TEST_VALID_BVID2]) > 10

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_fetch_missing(self, db):
        await db.fetch_from_video(TEST_MISSING_BVID)

    @pytest.mark.xfail
    @pytest.mark.asyncio
    async def test_fetch_invalid(self, db):
        await db.fetch_from_video(TEST_INVALID_BVID)

    @pytest.mark.asyncio
    async def test_excel_full(self, db):
        await db.fetch_from_video(TEST_VALID_BVID1)
        db.to_excel(TEST_EXCEL_FILENAME)
        assert os.path.exists(TEST_EXCEL_FILENAME)
        os.unlink(TEST_EXCEL_FILENAME)

    @pytest.mark.xfail
    def test_excel_empty(self, db):
        db.to_excel(TEST_EXCEL_FILENAME)
        assert os.path.exists(TEST_EXCEL_FILENAME)
        os.unlink(TEST_EXCEL_FILENAME)
