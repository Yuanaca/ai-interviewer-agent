<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold">仪表盘</h1>
      <p class="text-sm text-on-surface-variant mt-1">面试智能系统概览</p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="glass-card p-5 hover:border-primary/30 transition-all cursor-pointer" @click="$router.push('/interview')">
        <div class="flex items-center justify-between mb-3">
          <span class="material-symbols-outlined text-2xl" style="color: #c3c0ff;">videocam</span>
          <span class="text-xs font-mono text-on-surface-variant">总次数</span>
        </div>
        <div class="text-3xl font-bold text-primary">{{ stats.totalInterviews }}</div>
        <div class="text-xs text-on-surface-variant mt-1">面试会话</div>
      </div>

      <div class="glass-card p-5 hover:border-secondary/30 transition-all cursor-pointer" @click="$router.push('/jobs')">
        <div class="flex items-center justify-between mb-3">
          <span class="material-symbols-outlined text-2xl" style="color: #b3c5ff;">work</span>
          <span class="text-xs font-mono text-on-surface-variant">在招</span>
        </div>
        <div class="text-3xl font-bold text-secondary">{{ stats.totalJobs }}</div>
        <div class="text-xs text-on-surface-variant mt-1">职位</div>
      </div>

      <div class="glass-card p-5 hover:border-tertiary/30 transition-all cursor-pointer" @click="$router.push('/knowledge')">
        <div class="flex items-center justify-between mb-3">
          <span class="material-symbols-outlined text-2xl" style="color: #4edea3;">book</span>
          <span class="text-xs font-mono text-on-surface-variant">RAG</span>
        </div>
        <div class="text-3xl font-bold text-tertiary">{{ stats.totalKnowledge }}</div>
        <div class="text-xs text-on-surface-variant mt-1">知识条目</div>
      </div>

      <div class="glass-card p-5 hover:border-amber-400/30 transition-all cursor-pointer" @click="$router.push('/reports')">
        <div class="flex items-center justify-between mb-3">
          <span class="material-symbols-outlined text-2xl" style="color: #fbbf24;">assessment</span>
          <span class="text-xs font-mono text-on-surface-variant">报告</span>
        </div>
        <div class="text-3xl font-bold text-amber-400">{{ stats.totalReports }}</div>
        <div class="text-xs text-on-surface-variant mt-1">评估报告</div>
      </div>
    </div>

    <!-- 最近面试 + 快速操作 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 最近面试 -->
      <div class="lg:col-span-2 glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">history</span>
            最近面试
          </h2>
          <router-link to="/interview" class="btn-primary text-sm flex items-center gap-1.5">
            <span class="material-symbols-outlined text-lg">add</span>
            新建面试
          </router-link>
        </div>

        <div v-if="recentSessions.length === 0" class="text-center py-12 text-on-surface-variant">
          <span class="material-symbols-outlined text-4xl mb-3 block opacity-30">videocam_off</span>
          <p>暂无面试记录</p>
          <p class="text-xs mt-1">点击"新建面试"开始第一次 AI 面试</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="s in recentSessions"
            :key="s.session_id"
            class="flex items-center justify-between p-3 rounded-xl bg-surface-container hover:bg-surface-container-high transition-all cursor-pointer"
            @click="openSession(s)"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                :class="s.phase === 'completed' ? 'bg-tertiary/10' : 'bg-secondary/10'"
              >
                <span class="material-symbols-outlined text-lg"
                  :class="s.phase === 'completed' ? 'text-tertiary' : 'text-secondary'"
                >{{ s.phase === 'completed' ? 'check_circle' : 'pending' }}</span>
              </div>
              <div>
                <p class="text-sm font-medium truncate max-w-[200px]">
                  面试 #{{ s.session_id?.slice(-6) }}
                </p>
                <p class="text-xs text-on-surface-variant">
                  {{ s.phase === 'completed' ? '已完成' : '进行中' }}
                  · {{ (s.chat_history || []).filter(m => m.role === 'candidate').length }} 回答
                </p>
              </div>
            </div>
            <span class="material-symbols-outlined text-on-surface-variant text-lg">chevron_right</span>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="glass-card p-6 space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span class="material-symbols-outlined text-secondary">bolt</span>
          快速操作
        </h2>

        <button @click="$router.push('/interview')" class="w-full p-4 rounded-xl text-left transition-all"
          style="background: rgba(125, 211, 252, 0.06); border: 1px solid rgba(125, 211, 252, 0.1);">
          <span class="material-symbols-outlined text-xl text-primary mb-2 block">play_circle</span>
          <p class="font-semibold text-sm">开始新面试</p>
          <p class="text-xs text-on-surface-variant mt-1">创建 AI 驱动的面试会话</p>
        </button>

        <button @click="$router.push('/knowledge')" class="w-full p-4 rounded-xl text-left transition-all bg-surface-container hover:bg-surface-container-high border border-outline-variant/20">
          <span class="material-symbols-outlined text-xl text-tertiary mb-2 block">library_add</span>
          <p class="font-semibold text-sm">添加知识库</p>
          <p class="text-xs text-on-surface-variant mt-1">丰富 RAG 检索内容</p>
        </button>

        <button @click="$router.push('/jobs')" class="w-full p-4 rounded-xl text-left transition-all bg-surface-container hover:bg-surface-container-high border border-outline-variant/20">
          <span class="material-symbols-outlined text-xl text-secondary mb-2 block">post_add</span>
          <p class="font-semibold text-sm">发布新职位</p>
          <p class="text-xs text-on-surface-variant mt-1">管理招聘岗位信息</p>
        </button>

        <!-- RAG 索引状态 -->
        <div class="p-3 rounded-xl bg-surface-container">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs text-on-surface-variant">RAG 索引状态</span>
            <span class="badge badge-green text-[10px]">运行中</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="marching-ants flex-1"></div>
            <span class="text-[10px] font-mono text-on-surface-variant">ChromaDB</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { interviewAPI, jobsAPI, knowledgeAPI } from '@/api'

const router = useRouter()
const recentSessions = ref([])
const stats = ref({
  totalInterviews: 0,
  totalJobs: 0,
  totalKnowledge: 0,
  totalReports: 0,
})

function openSession(session) {
  if (session.phase === 'completed') {
    router.push(`/reports`)
  } else {
    router.push('/interview')
  }
}

onMounted(async () => {
  try {
    const [sessions, reports, jobs, knowledge] = await Promise.all([
      interviewAPI.listSessions(),
      interviewAPI.listReports(),
      jobsAPI.list(),
      knowledgeAPI.list(),
    ])
    recentSessions.value = (sessions.data || []).slice(0, 5)
    stats.value = {
      totalInterviews: (sessions.data || []).length,
      totalJobs: (jobs.data || []).length,
      totalKnowledge: (knowledge.data || []).length,
      totalReports: (reports.data || []).length,
    }
  } catch {
    // 后端离线
  }
})
</script>
