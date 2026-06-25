import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { interviewAPI } from '@/api'

/**
 * 面试会话 Store
 * 管理当前面试会话的状态
 */
export const useInterviewStore = defineStore('interview', () => {
  // ===== 会话状态 =====
  const sessionId = ref('')
  const phase = ref('init')
  const currentQuestionIndex = ref(0)
  const totalQuestions = ref(0)
  const currentQuestion = ref('')
  const questions = ref([])
  const chatHistory = ref([])
  const evaluations = ref([])
  const finalReport = ref(null)
  const resumeSummary = ref('')
  const resumeAnalysis = ref({})
  const errorMessage = ref('')

  // 加载中状态
  const isLoading = ref(false)

  // ===== 计算属性 =====
  const isCompleted = computed(() => phase.value === 'completed')
  const isAsking = computed(() => phase.value === 'asking')
  const progress = computed(() =>
    totalQuestions.value > 0
      ? Math.round((currentQuestionIndex.value / totalQuestions.value) * 100)
      : 0
  )

  const currentQuestionInfo = computed(() => {
    if (questions.value.length > 0 && currentQuestionIndex.value < questions.value.length) {
      return questions.value[currentQuestionIndex.value]
    }
    return null
  })

  const lastInterviewerMessage = computed(() => {
    const msgs = chatHistory.value.filter((m) => m.role === 'interviewer')
    return msgs.length > 0 ? msgs[msgs.length - 1].content : ''
  })

  // ===== 操作 =====

  /** 创建面试会话 */
  async function createSession(data) {
    isLoading.value = true
    errorMessage.value = ''
    try {
      const res = await interviewAPI.create(data)
      if (res.success) {
        _applyState(res.data)
      } else {
        errorMessage.value = res.message || '创建失败'
      }
      return res
    } catch (e) {
      errorMessage.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /** 提交回答 */
  async function submitAnswer(answer) {
    if (!sessionId.value) return
    isLoading.value = true
    errorMessage.value = ''
    try {
      const res = await interviewAPI.submitAnswer({
        session_id: sessionId.value,
        answer,
        question_index: currentQuestionIndex.value,
      })
      if (res.success) {
        _applyState(res.data)
      }
      return res
    } catch (e) {
      errorMessage.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /** 获取会话状态（恢复会话） */
  async function fetchState(id) {
    isLoading.value = true
    try {
      const res = await interviewAPI.getState(id)
      if (res.success) {
        _applyState(res.data)
      }
      return res
    } catch (e) {
      errorMessage.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /** 获取报告 */
  async function fetchReport(id) {
    try {
      const res = await interviewAPI.getReport(id || sessionId.value)
      if (res.success) {
        finalReport.value = res.data
      }
      return res
    } catch (e) {
      errorMessage.value = e.message
      throw e
    }
  }

  /** 重置 */
  function reset() {
    sessionId.value = ''
    phase.value = 'init'
    currentQuestionIndex.value = 0
    totalQuestions.value = 0
    currentQuestion.value = ''
    questions.value = []
    chatHistory.value = []
    evaluations.value = []
    finalReport.value = null
    resumeSummary.value = ''
    resumeAnalysis.value = {}
    errorMessage.value = ''
    isLoading.value = false
  }

  // ===== 内部方法 =====
  function _applyState(state) {
    sessionId.value = state.session_id
    phase.value = state.phase
    currentQuestionIndex.value = state.current_question_index
    totalQuestions.value = state.total_questions
    currentQuestion.value = state.current_question
    questions.value = state.questions || []
    chatHistory.value = state.chat_history || []
    evaluations.value = state.evaluations || []
    finalReport.value = state.final_report || null
    resumeSummary.value = state.resume_summary || ''
    resumeAnalysis.value = state.resume_analysis || {}
    errorMessage.value = state.error_message || ''
  }

  return {
    sessionId,
    phase,
    currentQuestionIndex,
    totalQuestions,
    currentQuestion,
    questions,
    chatHistory,
    evaluations,
    finalReport,
    resumeSummary,
    resumeAnalysis,
    errorMessage,
    isLoading,
    isCompleted,
    isAsking,
    progress,
    currentQuestionInfo,
    lastInterviewerMessage,
    createSession,
    submitAnswer,
    fetchState,
    fetchReport,
    reset,
  }
})
