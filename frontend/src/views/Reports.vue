<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">面试报告</h1>
      <p class="text-sm text-on-surface-variant mt-1">AI 生成的面试评估报告存档</p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <span class="material-symbols-outlined animate-spin text-3xl text-on-surface-variant">progress_activity</span>
    </div>

    <div v-else-if="reports.length === 0" class="glass-card p-12 text-center">
      <span class="material-symbols-outlined text-5xl text-on-surface-variant/30 mb-4 block">assessment</span>
      <p class="text-on-surface-variant">暂无面试报告</p>
      <router-link to="/interview" class="btn-primary inline-flex items-center gap-2 mt-4">
        <span class="material-symbols-outlined text-lg">play_arrow</span>开始面试
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="report in reports"
        :key="report.session_id"
        class="glass-card p-5 hover:border-primary/30 transition-all cursor-pointer"
        @click="viewReport(report)"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-xl flex items-center justify-center text-2xl font-bold"
              :class="getScoreBg(report.overall_score)"
            >{{ report.overall_score || report.report?.overall_score || 'N/A' }}</div>
            <div>
              <h3 class="font-semibold">{{ report.job_title || '未指定职位' }}</h3>
              <p class="text-xs text-on-surface-variant mt-0.5">
                面试 #{{ (report.session_id || '').slice(-8) }}
                · {{ report.created_at?.slice(0, 10) || '' }}
              </p>
              <div class="flex items-center gap-2 mt-1.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-medium"
                  :class="getRecBadge(report.recommendation || report.report?.recommendation)"
                >{{ recLabel(report.recommendation || report.report?.recommendation) }}</span>
              </div>
            </div>
          </div>
          <span class="material-symbols-outlined text-on-surface-variant">chevron_right</span>
        </div>
      </div>
    </div>

    <!-- 报告详情弹窗 -->
    <div v-if="selectedReport" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="selectedReport = null">
      <div class="glass-card-elevated w-full max-w-xl mx-4 p-6 space-y-4 max-h-[85vh] overflow-y-auto">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold">面试报告详情</h2>
          <button @click="selectedReport = null" class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-surface-container">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="text-center py-3">
          <div class="text-4xl font-bold" :class="getScoreColor(selectedReport.overall_score)">
            {{ selectedReport.overall_score || selectedReport.report?.overall_score || 'N/A' }}
          </div>
          <span class="text-xs text-on-surface-variant">/ 100 总体评分</span>
        </div>

        <div v-if="selectedReport.scores_by_dimension || selectedReport.report?.scores_by_dimension" class="grid grid-cols-2 gap-2">
          <div v-for="(score, dim) in (selectedReport.scores_by_dimension || selectedReport.report?.scores_by_dimension || {})" :key="dim"
            class="flex justify-between items-center p-2 rounded bg-surface-container">
            <span class="text-xs text-on-surface-variant">{{ dimLabels[dim] || dim }}</span>
            <span class="text-sm font-bold" :class="getScoreColor(score)">{{ score }}</span>
          </div>
        </div>

        <div>
          <h3 class="text-sm font-semibold mb-2 text-tertiary">优势</h3>
          <ul class="space-y-1">
            <li v-for="(s, i) in (selectedReport.strengths || selectedReport.report?.strengths || [])" :key="i" class="text-sm flex gap-1.5">
              <span class="text-tertiary">•</span>{{ s }}
            </li>
          </ul>
        </div>

        <div>
          <h3 class="text-sm font-semibold mb-2 text-amber-400">待改进</h3>
          <ul class="space-y-1">
            <li v-for="(w, i) in (selectedReport.weaknesses || selectedReport.report?.weaknesses || [])" :key="i" class="text-sm flex gap-1.5">
              <span class="text-amber-400">•</span>{{ w }}
            </li>
          </ul>
        </div>

        <div>
          <h3 class="text-sm font-semibold mb-2">综合评价</h3>
          <p class="text-sm text-on-surface-variant leading-relaxed">{{ selectedReport.summary || selectedReport.report?.summary || '暂无' }}</p>
        </div>

        <button @click="selectedReport = null" class="btn-secondary w-full">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { interviewAPI } from '@/api'

const reports = ref([])
const loading = ref(true)
const selectedReport = ref(null)

const dimLabels = {
  technical: '技术能力', communication: '沟通表达', experience: '项目经验',
  learning: '学习能力', culture_fit: '文化契合',
}

function getScoreBg(score) {
  if (score >= 80) return 'bg-tertiary/15 text-tertiary'
  if (score >= 60) return 'bg-secondary/15 text-secondary'
  return 'bg-amber-400/15 text-amber-400'
}

function getScoreColor(score) {
  if (score >= 80) return 'text-tertiary'
  if (score >= 60) return 'text-secondary'
  return 'text-amber-400'
}

function getRecBadge(rec) {
  if (rec === 'strong_hire') return 'bg-tertiary/15 text-tertiary'
  if (rec === 'hire') return 'bg-secondary/15 text-secondary'
  if (rec === 'weak_hire') return 'bg-amber-400/15 text-amber-400'
  return 'bg-error/15 text-error'
}

function recLabel(rec) {
  const map = { strong_hire: '强烈推荐', hire: '推荐录用', weak_hire: '可考虑', no_hire: '不建议' }
  return map[rec] || rec || '未评定'
}

function viewReport(report) {
  selectedReport.value = report
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await interviewAPI.listReports()
    reports.value = res.data || []
  } catch {
    reports.value = []
  } finally {
    loading.value = false
  }
})
</script>
