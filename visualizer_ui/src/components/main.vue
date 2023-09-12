<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import {computed, ref} from "vue"
import api from '../api'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const keyword = ref('日本排放核废水')
const excelFilename = ref('excel_db.xlsx')
const fetchCount = ref(300)
const showStatistics = ref(false)
const isFetching = ref(false)
const wordcloudUrl = computed(() =>
    showStatistics.value ? wordcloudBaseUrl + wordcloudRand.value.toString() : undefined)
const wordcloudRand = ref(0)
const wordcloudBaseUrl = 'http://localhost:8080/api/wordcloud?width=800&height=400&rand='
const chart_data = ref({
  labels: ['default'],
  datasets: [ {
    label: '弹幕数量',
    backgroundColor: '#70a1ff',
    data: [1]
  } ]
})

const fetchDanmakus = (_evt: SubmitEvent | Event) => {
  isFetching.value = true
  showStatistics.value = false
  api.fetch(keyword.value, fetchCount.value)
      .then(() => api.top_danmakus(20))
      .then(result => {
        chart_data.value.labels = []
        chart_data.value.datasets[0].data = []
        result.forEach(v => {
          chart_data.value.labels.push(v.danmaku)
          chart_data.value.datasets[0].data.push(v.count)
        })
        wordcloudRand.value = Math.random()
        isFetching.value = false
        showStatistics.value = true
      }).catch(() => { isFetching.value = false })
}



</script>

<template>
  <main class="q-ma-md">
    <q-form @submit="fetchDanmakus">
      <q-input label="关键字" v-model="keyword" :rules="[(val: string) => val !== '' || '关键字不能为空']" :loading="isFetching" :disable="isFetching"></q-input>
      <q-input type="number" label="视频数量" v-model="fetchCount" :rules="[(val: number) => val > 0 || '视频数量必须大于0']" :loading="isFetching" :disable="isFetching"></q-input>
      <q-input label="Excel文件名" v-model="excelFilename" :rules="[(val: string) => val !== '' || 'Excel文件名不能为空']" :loading="isFetching" :disable="isFetching"></q-input>
      <q-btn class="q-mt-md q-mb-md" type="submit" color="primary" label="分析" :loading="isFetching" />
      <q-btn class="q-mt-md q-mb-md q-ml-sm" color="secondary" label="导出Excel表" :disable="!showStatistics" />
    </q-form>
    <hr />
    <div v-if="showStatistics" class="flex column col">
      <h1 class="statistics-title row">总体统计信息</h1>
      <div class="row">
        <div class="statistics-container">
          <p>云图</p>
          <q-img :src="wordcloudUrl" height="350" />
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
  height: 350px;
}
</style>