<script setup lang="ts">
import { useQuasar } from "quasar"
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import {computed, ref} from "vue"
import api from '../api'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const $q = useQuasar()
const keyword = ref('日本核污染水排海')
const excelFilename = ref('excel_db.xlsx')
const fetchCount = ref(300)
const showStatistics = ref(false)
const isFetching = ref(false)
const isExporting = ref(false)
const wordcloudUrl = computed(() =>
    showStatistics.value ? wordcloudBaseUrl + wordcloudRand.value.toString() : undefined)
const wordcloudRand = ref(0)
const wordcloudBaseUrl = 'http://localhost:8080/api/wordcloud?rand='
const chart_data = ref({
  labels: ['default'],
  datasets: [ {
    label: '弹幕数量',
    backgroundColor: '#70a1ff',
    data: [1]
  } ]
})

const exportExcel = () => {
  isExporting.value = true
  api.exportExcel(excelFilename.value).then(() => {
    $q.notify({
      type: 'positive',
      message: 'Excel表导出成功'
    })
    isExporting.value = false
  }).catch(() => {
    $q.notify({
      type: 'negative',
      message: '导出接口调用出错，导出失败'
    })
    isExporting.value = false
  })
}

const fetchDanmakus = (_evt: SubmitEvent | Event) => {
  isFetching.value = true
  showStatistics.value = false
  const startTime = new Date()
  api.fetch(keyword.value, fetchCount.value)
      .then(() => api.topDanmakus(20))
      .then(result => {
        chart_data.value.labels = []
        chart_data.value.datasets[0].data = []
        result.forEach(v => {
          chart_data.value.labels.push(v.danmaku)
          chart_data.value.datasets[0].data.push(v.count)
        })
        wordcloudRand.value = Math.random() //强制重新加载图片
        isFetching.value = false
        showStatistics.value = true
        const endTime = new Date()
        $q.notify({
          type: 'positive',
          message: `弹幕数据分析完毕，本次共耗时${(endTime.getTime() - startTime.getTime()) / 1000}秒`
        })
      }).catch(() => {
        isFetching.value = false
        $q.notify({
          type: 'negative',
          message: '弹幕数据分析接口调用出错，分析失败'
        })
      })
}



</script>

<template>
  <main class="q-ma-md">
    <q-form @submit="fetchDanmakus">
      <q-input label="关键字" v-model="keyword" :rules="[(val: string) => val !== '' || '关键字不能为空']" :disable="isFetching"></q-input>
      <q-input type="number" label="视频数量" v-model="fetchCount" :rules="[(val: number) => val > 0 || '视频数量必须大于0']" :disable="isFetching"></q-input>
      <q-input label="Excel文件名" v-model="excelFilename" :rules="[(val: string) => val !== '' || 'Excel文件名不能为空']" :disable="isExporting"></q-input>
      <q-btn class="q-mt-md q-mb-md" type="submit" color="primary" label="分析" :loading="isFetching" />
      <q-btn class="q-mt-md q-mb-md q-ml-sm" @click="exportExcel" color="secondary" label="导出Excel表" :disable="!showStatistics" :loading="isExporting" />
    </q-form>
    <hr />
    <div v-if="showStatistics" class="flex column col">
      <h1 class="statistics-title row">分析结果</h1>
      <div class="row">
        <div class="statistics-container">
          <p>云图</p>
          <q-img :src="wordcloudUrl" height="500" width="500" />
        </div>
        <div class="statistics-container">
          <p>弹幕统计图</p>
          <div class="chart">
            <bar :data="chart_data" :options="{maintainAspectRatio: false}" />
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.statistics-title {
  margin: 0;
  font-size: 2em;
}

.statistics-container {
  width: 50%;
  padding: 0 10px;
}

.chart {
  position: relative;
  height: 600px;
}
</style>