import {request} from "../utils"

interface DanmakuFrequency {
    danmaku: string,
    count: number
}

export default {
    async fetch(keyword: string, n: number){
        await request({
            url: '/fetch',
            method: 'get',
            params: { keyword, n }
        })
    },

    async top_danmakus(n: number): Promise<[DanmakuFrequency]>{
        const response = await request({
            url: '/top_danmakus',
            method: 'get',
            params: { n }
        })
        return response.data.top_danmakus
    }
}