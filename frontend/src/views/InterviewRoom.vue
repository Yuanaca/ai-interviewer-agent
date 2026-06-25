<template>
  <div class="max-w-5xl mx-auto space-y-6">
    <!-- 顶部标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">面试室</h1>
        <p class="text-sm text-on-surface-variant mt-1">AI 驱动的智能面试会话</p>
      </div>
      <button
        v-if="store.sessionId && !store.isCompleted"
        @click="store.reset()"
        class="btn-secondary flex items-center gap-2 text-sm"
      >
        <span class="material-symbols-outlined text-lg">restart_alt</span>
        重新开始
      </button>
    </div>

    <!-- 1. 面试配置表单（未开始时） -->
    <div v-if="!store.sessionId" class="glass-card p-6 space-y-5">
      <h2 class="text-lg font-semibold flex items-center gap-2">
        <span class="material-symbols-outlined text-primary">edit_note</span>
        配置面试
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- 职位选择 -->
        <div>
          <label class="block text-sm font-medium mb-2">选择职位</label>
          <select v-model="selectedJobId" class="input-field">
            <option value="">-- 手动输入职位信息 --</option>
            <option v-for="j in jobList" :key="j.id" :value="j.id">{{ j.title }} - {{ j.department }}</option>
          </select>
        </div>

        <!-- 面试类型 -->
        <div>
          <label class="block text-sm font-medium mb-2">面试类型</label>
          <select v-model="form.interview_type" class="input-field">
            <option value="technical">技术面试</option>
            <option value="behavioral">行为面试</option>
            <option value="mixed">综合面试</option>
          </select>
        </div>

        <!-- 题目数量 -->
        <div>
          <label class="block text-sm font-medium mb-2">题目数量</label>
          <select v-model.number="form.question_count" class="input-field">
            <option :value="3">3 题</option>
            <option :value="5">5 题</option>
            <option :value="8">8 题</option>
            <option :value="10">10 题</option>
          </select>
        </div>

        <!-- 语言 -->
        <div>
          <label class="block text-sm font-medium mb-2">面试语言</label>
          <div class="flex gap-2">
            <button
              v-for="l in [{v:'zh',n:'中文'},{v:'en',n:'English'}]"
              :key="l.v"
              @click="form.language = l.v"
              class="flex-1 px-4 py-2 rounded-lg text-sm border transition-all"
              :class="form.language === l.v ? 'border-primary bg-primary/10 text-primary' : 'border-outline-variant/30 text-on-surface-variant'"
            >{{ l.n }}</button>
          </div>
        </div>
      </div>

      <!-- 手动职位信息 -->
      <div v-if="!selectedJobId" class="space-y-4 pt-2">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">职位名称</label>
            <input v-model="form.job_title" placeholder="如：高级前端工程师" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">部门</label>
            <input v-model="form.job_department" placeholder="如：技术部" class="input-field" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">职位描述</label>
          <textarea v-model="form.job_description" rows="2" placeholder="描述岗位职责和要求..." class="input-field resize-none"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">技能要求（逗号分隔）</label>
          <input v-model="form.job_skills" placeholder="如：React, TypeScript, Node.js" class="input-field" />
        </div>
      </div>

      <!-- 简历上传 -->
      <div class="pt-2">
        <label class="block text-sm font-medium mb-2">候选人简历</label>
        <textarea
          v-model="form.resume_text"
          rows="5"
          placeholder="粘贴简历内容或上传 PDF 文件...&#10;&#10;支持纯文本简历粘贴"
          class="input-field resize-none font-mono text-sm"
        ></textarea>
        <div class="mt-2 flex items-center gap-3">
          <label class="btn-secondary text-sm flex items-center gap-1.5 cursor-pointer">
            <span class="material-symbols-outlined text-lg">upload_file</span>
            上传简历（支持图片 OCR）
            <input type="file" accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg,.bmp,.webp" @change="handleFileUpload" class="hidden" />
          </label>
          <span v-if="uploadStatus" class="text-xs" :class="uploadStatus === 'ok' ? 'text-tertiary' : 'text-error'">
            {{ uploadStatus === 'ok' ? '✅ 简历已加载 (' + form.resume_text.length + ' 字符)' : '❌ ' + uploadError }}
          </span>
          <span v-else-if="form.resume_text" class="text-xs text-on-surface-variant">
            已输入 {{ form.resume_text.length }} 字符
          </span>
        </div>
      </div>

      <!-- 知识库选择 -->
      <div v-if="knowledgeItems.length > 0" class="pt-2">
        <label class="block text-sm font-medium mb-2">关联知识库（用于 RAG 增强）</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="item in knowledgeItems"
            :key="item.id"
            @click="toggleKnowledge(item)"
            class="px-3 py-1.5 rounded-lg text-xs border transition-all"
            :class="selectedKnowledge.includes(item.id)
              ? 'border-secondary bg-secondary/10 text-secondary'
              : 'border-outline-variant/30 text-on-surface-variant hover:border-outline'"
          >
            {{ item.title }}
          </button>
        </div>
      </div>

      <!-- 开始按钮 -->
      <div class="pt-4 flex items-center gap-3">
        <button
          @click="startInterview"
          :disabled="isStarting || !settings.apiKey"
          class="btn-primary flex items-center gap-2 text-base px-8 py-3"
        >
          <span v-if="isStarting" class="material-symbols-outlined animate-spin text-lg">progress_activity</span>
          <span v-else class="material-symbols-outlined text-lg">play_arrow</span>
          {{ isStarting ? '正在生成面试问题...' : '开始面试' }}
        </button>
        <p v-if="!settings.apiKey" class="text-xs text-amber-400">
          ⚠️ 请先在
          <router-link to="/settings" class="underline text-primary">设置</router-link>
          中配置 API Key
        </p>
      </div>
    </div>

    <!-- 2. 面试进行中 -->
    <div v-if="store.sessionId && !store.isCompleted" class="space-y-6">
      <!-- 进度条 -->
      <div class="glass-card p-4">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="pulse-dot"></span>
            <span class="text-sm font-medium">面试进行中</span>
          </div>
          <span class="text-sm font-mono text-secondary">
            {{ store.currentQuestionIndex + 1 }} / {{ store.totalQuestions }}
          </span>
        </div>
        <div class="w-full h-1.5 rounded-full bg-surface-container">
          <div
            class="h-full rounded-full transition-all duration-500"
            style="background: rgba(125, 211, 252, 0.4);"
            :style="{ width: ((store.currentQuestionIndex + 1) / store.totalQuestions * 100) + '%' }"
          ></div>
        </div>
      </div>

      <!-- 简历分析卡片 -->
      <div v-if="store.resumeAnalysis && Object.keys(store.resumeAnalysis).length > 0" class="glass-card p-4">
        <div class="flex items-center gap-2 mb-3">
          <span class="material-symbols-outlined text-primary text-lg">description</span>
          <span class="text-sm font-semibold">简历分析结果</span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div class="p-2 rounded-lg bg-surface-container">
            <span class="text-xs text-on-surface-variant block mb-0.5">候选人</span>
            <span class="font-medium">{{ store.resumeAnalysis.name || '未知' }}</span>
          </div>
          <div class="p-2 rounded-lg bg-surface-container">
            <span class="text-xs text-on-surface-variant block mb-0.5">经验</span>
            <span class="font-medium">{{ store.resumeAnalysis.years_of_experience || '未知' }}年</span>
          </div>
          <div class="p-2 rounded-lg bg-surface-container">
            <span class="text-xs text-on-surface-variant block mb-0.5">学历</span>
            <span class="font-medium">{{ store.resumeAnalysis.education || '未知' }}</span>
          </div>
          <div class="p-2 rounded-lg bg-surface-container">
            <span class="text-xs text-on-surface-variant block mb-0.5">技能数</span>
            <span class="font-medium">{{ (store.resumeAnalysis.skills || []).length }} 项</span>
          </div>
        </div>
        <div v-if="(store.resumeAnalysis.skills || []).length > 0" class="flex flex-wrap gap-1.5 mt-3">
          <span v-for="s in store.resumeAnalysis.skills.slice(0, 8)" :key="s" class="badge badge-blue text-[11px]">{{ s }}</span>
        </div>
      </div>

      <!-- 对话区 -->
      <div class="glass-card p-6 space-y-4 min-h-[400px] max-h-[500px] overflow-y-auto" ref="chatContainer">
        <div
          v-for="(msg, i) in displayMessages"
          :key="i"
          class="flex gap-3"
          :class="msg.role === 'candidate' ? 'justify-end' : ''"
        >
          <!-- 面试官消息 -->
          <template v-if="msg.role === 'interviewer' || msg.role === 'system'">
            <div class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center"
              :class="msg.role === 'system' ? 'bg-surface-container' : ''"
              :style="msg.role === 'interviewer' ? 'background: rgba(125, 211, 252, 0.2); border: 1px solid rgba(125, 211, 252, 0.25);' : ''"
            >
              <span class="material-symbols-outlined text-white text-sm">
                {{ msg.role === 'system' ? 'info' : 'smart_toy' }}
              </span>
            </div>
            <div class="max-w-[75%]">
              <div class="text-xs text-on-surface-variant mb-1">
                {{ msg.role === 'system' ? '系统' : 'AI 面试官' }}
                <span v-if="msg.role === 'system' && i === displayMessages.length - 1" class="inline-flex items-center gap-1 ml-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
                  <span class="text-secondary text-xs">分析中</span>
                </span>
              </div>
              <div class="px-4 py-2.5 rounded-xl text-sm leading-relaxed"
                :class="msg.role === 'system' ? 'bg-surface-container text-on-surface-variant' : ''"
                :style="msg.role === 'interviewer' ? 'background: rgba(15, 21, 36, 0.8); border: 1px solid rgba(125, 211, 252, 0.08);' : ''"
              >{{ msg.content }}</div>
            </div>
          </template>

          <!-- 候选人消息 -->
          <template v-if="msg.role === 'candidate'">
            <div class="max-w-[75%]">
              <div class="text-xs text-right text-on-surface-variant mb-1">候选人</div>
              <div class="px-4 py-2.5 rounded-xl text-sm leading-relaxed"
                style="background: rgba(125, 211, 252, 0.08); border: 1px solid rgba(125, 211, 252, 0.12);"
              >{{ msg.content }}</div>
            </div>
            <div class="w-8 h-8 rounded-lg flex-shrink-0 bg-primary/20 flex items-center justify-center">
              <span class="material-symbols-outlined text-primary text-sm">person</span>
            </div>
          </template>
        </div>

        <!-- 加载指示器 -->
        <div v-if="store.isLoading" class="flex gap-3">
          <div class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center opacity-60">
            <span class="material-symbols-outlined text-white text-sm">smart_toy</span>
          </div>
          <div class="px-4 py-2.5 rounded-xl bg-surface-container-high">
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-secondary animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 rounded-full bg-secondary animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 rounded-full bg-secondary animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div v-if="store.isAsking" class="glass-card p-4">
        <div class="flex gap-3">
          <textarea
            v-model="userAnswer"
            placeholder="输入你的回答..."
            rows="3"
            class="input-field flex-1 resize-none"
            :disabled="store.isLoading"
            @keydown.ctrl.enter="sendAnswer"
          ></textarea>
          <button
            @click="sendAnswer"
            :disabled="!userAnswer.trim() || store.isLoading"
            class="btn-primary flex items-center gap-2 self-end px-6"
          >
            <span v-if="store.isLoading" class="material-symbols-outlined animate-spin text-lg">progress_activity</span>
            <span v-else>发送</span>
            <span class="text-xs opacity-60">Ctrl+Enter</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 3. 面试完成 - 报告 -->
    <div v-if="store.isCompleted && store.finalReport" class="space-y-6">
      <div class="glass-card p-8 text-center">
        <div class="w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-4" style="background: rgba(200, 160, 240, 0.1); border: 1px solid rgba(200, 160, 240, 0.2);">
          <span class="material-symbols-outlined text-tertiary text-3xl">check_circle</span>
        </div>
        <h2 class="text-xl font-bold mb-2">面试已完成！</h2>
        <p class="text-on-surface-variant text-sm mb-4">以下是 AI 生成的综合评估报告</p>
        <div class="inline-flex items-center gap-3 px-5 py-3 rounded-xl bg-surface-container">
          <span class="text-3xl font-bold" :class="scoreColor">{{ store.finalReport.overall_score || store.finalReport.report?.overall_score || 0 }}</span>
          <span class="text-sm text-on-surface-variant">/ 100 总体评分</span>
        </div>
      </div>

      <!-- 各维度评分 -->
      <div class="glass-card p-6">
        <h3 class="text-base font-semibold mb-4 flex items-center gap-2">
          <span class="material-symbols-outlined text-secondary">radar</span>
          各维度评分
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div
            v-for="(score, dim) in (store.finalReport.scores_by_dimension || store.finalReport.report?.scores_by_dimension || {})"
            :key="dim"
            class="text-center p-3 rounded-xl bg-surface-container"
          >
            <div class="text-2xl font-bold mb-1" :class="getScoreColorClass(score)">{{ score }}</div>
            <div class="text-xs text-on-surface-variant">{{ dimLabels[dim] || dim }}</div>
          </div>
        </div>
      </div>

      <!-- 优劣势 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="glass-card p-6">
          <h3 class="text-base font-semibold mb-3 flex items-center gap-2 text-tertiary">
            <span class="material-symbols-outlined">thumb_up</span>
            核心优势
          </h3>
          <ul class="space-y-2">
            <li
              v-for="(s, i) in (store.finalReport.strengths || store.finalReport.report?.strengths || [])"
              :key="i"
              class="flex items-start gap-2 text-sm"
            >
              <span class="text-tertiary mt-0.5">•</span>
              {{ s }}
            </li>
          </ul>
        </div>
        <div class="glass-card p-6">
          <h3 class="text-base font-semibold mb-3 flex items-center gap-2 text-amber-400">
            <span class="material-symbols-outlined">lightbulb</span>
            待改进
          </h3>
          <ul class="space-y-2">
            <li
              v-for="(w, i) in (store.finalReport.weaknesses || store.finalReport.report?.weaknesses || [])"
              :key="i"
              class="flex items-start gap-2 text-sm"
            >
              <span class="text-amber-400 mt-0.5">•</span>
              {{ w }}
            </li>
          </ul>
        </div>
      </div>

      <!-- 综合评价 -->
      <div class="glass-card p-6">
        <h3 class="text-base font-semibold mb-3 flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">description</span>
          综合评价
        </h3>
        <p class="text-sm leading-relaxed text-on-surface-variant">
          {{ store.finalReport.summary || store.finalReport.report?.summary || '暂无' }}
        </p>
      </div>

      <!-- 录用建议 -->
      <div class="glass-card p-6 flex items-center justify-between">
        <div>
          <h3 class="text-base font-semibold">录用建议</h3>
        </div>
        <span class="px-4 py-2 rounded-lg text-sm font-bold" :class="recommendationClass">
          {{ recommendationText }}
        </span>
      </div>

      <!-- 逐题详情 -->
      <div class="glass-card p-6">
        <h3 class="text-base font-semibold mb-4 flex items-center gap-2">
          <span class="material-symbols-outlined text-on-surface-variant">list_alt</span>
          逐题评估详情
        </h3>
        <div class="space-y-4">
          <div
            v-for="(q, i) in store.questions"
            :key="i"
            class="p-4 rounded-xl bg-surface-container"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="badge badge-blue">{{ q.category || '题目' }}</span>
                <span class="text-xs text-on-surface-variant">{{ q.difficulty }}</span>
              </div>
              <span class="font-mono font-bold text-sm" :class="getEvalScoreClass(i)">
                {{ store.evaluations[i]?.score || '-' }}/100
              </span>
            </div>
            <p class="text-sm font-medium mb-2">Q{{ i + 1 }}: {{ q.question }}</p>
            <p v-if="candidateAnswers[i]" class="text-xs text-on-surface-variant mt-2 p-2 rounded border-l-2"
              style="background: rgba(125, 211, 252, 0.04); border-color: rgba(125, 211, 252, 0.3);">
              <span class="text-[10px] text-primary/70 block mb-1">候选人回答：</span>
              {{ candidateAnswers[i] }}
            </p>
            <p v-if="store.evaluations[i]?.feedback" class="text-xs text-on-surface-variant mt-2 p-2 rounded bg-background/50">
              <span class="text-[10px] text-tertiary/70 block mb-1">AI 评估：</span>
              {{ store.evaluations[i].feedback }}
            </p>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex gap-3">
        <button @click="store.reset()" class="btn-primary flex items-center gap-2">
          <span class="material-symbols-outlined text-lg">replay</span>
          开始新面试
        </button>
        <router-link to="/reports" class="btn-secondary flex items-center gap-2">查看所有报告</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useInterviewStore } from '@/stores/interview'
import { useSettingsStore } from '@/stores/settings'
import { jobsAPI, knowledgeAPI } from '@/api'

const store = useInterviewStore()
const settings = useSettingsStore()

// 表单
const selectedJobId = ref('')
const form = ref({
  interview_type: settings.defaultInterviewType,
  question_count: settings.defaultQuestionCount,
  language: settings.defaultLanguage,
  job_title: '',
  job_department: '',
  job_description: '',
  job_skills: '',
  resume_text: '',
})

const userAnswer = ref('')
const isStarting = ref(false)
const selectedKnowledge = ref([])
const jobList = ref([])
const knowledgeItems = ref([])
const chatContainer = ref(null)
const uploadStatus = ref('')   // '' | 'ok' | 'error'
const uploadError = ref('')

// 从聊天记录中提取候选人回答列表
const candidateAnswers = computed(() => {
  return store.chatHistory
    .filter(m => m.role === 'candidate')
    .map(m => m.content)
})

// 标签映射
const dimLabels = {
  technical: '技术能力',
  communication: '沟通表达',
  experience: '项目经验',
  learning: '学习能力',
  culture_fit: '文化契合',
}

// 显示消息（过滤系统消息）
const displayMessages = computed(() => {
  return store.chatHistory.filter(m => m.role !== 'system' || m.content.includes('评分') || m.content.includes('完成'))
})

// 评分颜色
const scoreColor = computed(() => {
  const report = store.finalReport || {}
  const score = report.overall_score || report.report?.overall_score || 0
  if (score >= 80) return 'text-tertiary'
  if (score >= 60) return 'text-secondary'
  return 'text-amber-400'
})

const recommendationClass = computed(() => {
  const report = store.finalReport || {}
  const rec = report.recommendation || report.report?.recommendation || ''
  if (rec === 'strong_hire') return 'bg-tertiary/15 text-tertiary border border-tertiary/30'
  if (rec === 'hire') return 'bg-secondary/15 text-secondary border border-secondary/30'
  if (rec === 'weak_hire') return 'bg-amber-400/15 text-amber-400 border border-amber-400/30'
  return 'bg-error/15 text-error border border-error/30'
})

const recommendationText = computed(() => {
  const rec = (store.finalReport || {}).recommendation || (store.finalReport || {}).report?.recommendation || ''
  const map = { strong_hire: '强烈推荐', hire: '推荐录用', weak_hire: '可考虑', no_hire: '不建议录用' }
  return map[rec] || rec || '暂无'
})

function getScoreColorClass(score) {
  if (score >= 80) return 'text-tertiary'
  if (score >= 60) return 'text-secondary'
  return 'text-amber-400'
}

function getEvalScoreClass(idx) {
  const score = store.evaluations[idx]?.score || 0
  if (score >= 80) return 'text-tertiary'
  if (score >= 60) return 'text-secondary'
  return 'text-amber-400'
}

function toggleKnowledge(item) {
  const idx = selectedKnowledge.value.indexOf(item.id)
  if (idx >= 0) selectedKnowledge.value.splice(idx, 1)
  else selectedKnowledge.value.push(item.id)
}

async function handleFileUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return

  uploadStatus.value = ''
  uploadError.value = ''

  const mime = file.type
  const name = file.name.toLowerCase()

  const isImage = mime.startsWith('image/') || /\.(png|jpe?g|gif|bmp|webp)$/i.test(name)

  // 图片 — 调用 OCR 识别
  if (isImage) {
    uploadStatus.value = 'error'
    uploadError.value = 'OCR 识别中，请稍候...'

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch('/api/interview/resume/ocr', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'OCR 识别失败')
      }

      const data = await res.json()
      if (data.success && data.data?.text) {
        form.value.resume_text = data.data.text
        uploadStatus.value = 'ok'
      } else {
        throw new Error('图片中未识别到文字')
      }
    } catch (e) {
      uploadStatus.value = 'error'
      uploadError.value = e.message || 'OCR 识别失败，请尝试粘贴文字'
    }
    return
  }

  // 检测视频/音频等二进制文件
  if (mime.startsWith('video/') || mime.startsWith('audio/') || /\.(mp[34]|avi|mov|wav|zip|rar|7z|exe)$/i.test(name)) {
    uploadStatus.value = 'error'
    uploadError.value = '不支持的文件格式，请上传 .txt 或 .pdf 简历'
    return
  }

  try {
    // PDF 文件 — 发送到后端提取文本
    if (mime === 'application/pdf' || name.endsWith('.pdf')) {
      uploadStatus.value = 'error'
      uploadError.value = 'PDF 解析中，请稍候...'

      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch('/api/interview/resume/extract-pdf', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'PDF 解析失败')
      }

      const data = await res.json()
      if (data.success && data.data?.text) {
        form.value.resume_text = data.data.text
        uploadStatus.value = 'ok'
      } else {
        throw new Error('PDF 中未检测到文字')
      }
      return
    }

    // 纯文本文件 — 直接读取
    const text = await file.text()

    // 文本有效性检测：如果包含过多乱码字符则拒绝
    const garbageRatio = _detectGarbage(text)
    if (garbageRatio > 0.3) {
      uploadStatus.value = 'error'
      uploadError.value = '文件内容似乎不是有效的文本简历（检测到 ' + Math.round(garbageRatio * 100) + '% 乱码），请上传纯文本或 PDF 文件'
      return
    }

    form.value.resume_text = text
    uploadStatus.value = 'ok'
  } catch (e) {
    uploadStatus.value = 'error'
    uploadError.value = e.message || '文件读取失败'
  }
}

/** 检测文本中乱码/二进制垃圾的比例 */
function _detectGarbage(text) {
  if (!text || text.length < 10) return 0
  const sample = text.slice(0, 2000)
  let garbage = 0
  for (const ch of sample) {
    const code = ch.charCodeAt(0)
    // 控制字符（除了常见空白）和私有区字符视为乱码
    if ((code < 0x20 && code !== 0x0a && code !== 0x0d && code !== 0x09) ||
        (code >= 0x80 && code < 0xA0) ||
        code === 0xFFFD) {
      garbage++
    }
  }
  return garbage / sample.length
}

async function startInterview() {
  if (!settings.apiKey) {
    alert('请先在设置中配置 API Key')
    return
  }
  isStarting.value = true

  const jobPosition = selectedJobId.value
    ? jobList.value.find(j => j.id === selectedJobId.value)
    : {
        title: form.value.job_title || '未指定职位',
        department: form.value.job_department,
        description: form.value.job_description,
        skills_required: (form.value.job_skills || '').split(',').map(s => s.trim()).filter(Boolean),
      }

  const selectedItems = knowledgeItems.value.filter(k => selectedKnowledge.value.includes(k.id))

  try {
    await store.createSession({
      job_position: jobPosition,
      resume_text: form.value.resume_text,
      interview_type: form.value.interview_type,
      question_count: form.value.question_count,
      language: form.value.language,
      llm_config: settings.getLLMConfig(),
      knowledge_items: selectedItems,
    })
  } catch (e) {
    alert('创建面试失败: ' + e.message)
  } finally {
    isStarting.value = false
  }
}

async function sendAnswer() {
  if (!userAnswer.value.trim() || store.isLoading) return
  const answer = userAnswer.value.trim()
  userAnswer.value = ''
  try {
    await store.submitAnswer(answer)
  } catch (e) {
    alert('提交失败: ' + e.message)
    userAnswer.value = answer // 恢复
  }
}

// 自动滚动到底部
watch(() => store.chatHistory.length, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
})

onMounted(async () => {
  try {
    const [jobRes, kbRes] = await Promise.all([
      jobsAPI.list(),
      knowledgeAPI.list(),
    ])
    jobList.value = jobRes.data || []
    knowledgeItems.value = kbRes.data || []
  } catch {
    // 后端未连接时静默失败
  }
})
</script>
