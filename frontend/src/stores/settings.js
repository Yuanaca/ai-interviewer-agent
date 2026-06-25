import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 全局设置 Store
 * 管理 LLM 模型选择、API Key 等配置
 * 数据持久化到 localStorage
 */
export const useSettingsStore = defineStore('settings', () => {
  // ===== LLM 配置 =====
  const provider = ref(localStorage.getItem('llm_provider') || 'openai')
  const modelName = ref(localStorage.getItem('llm_model') || 'gpt-4o-mini')
  const apiKey = ref(localStorage.getItem('llm_api_key') || '')
  const baseUrl = ref(localStorage.getItem('llm_base_url') || '')
  const temperature = ref(Number(localStorage.getItem('llm_temperature') || '0.7'))
  const maxTokens = ref(Number(localStorage.getItem('llm_max_tokens') || '4096'))

  // ===== 面试默认配置 =====
  const defaultQuestionCount = ref(Number(localStorage.getItem('default_question_count') || '5'))
  const defaultLanguage = ref(localStorage.getItem('default_language') || 'zh')
  const defaultInterviewType = ref(localStorage.getItem('default_interview_type') || 'technical')

  // 可用的模型提供商列表
  const providers = [
    { value: 'openai', label: 'OpenAI', models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
    { value: 'deepseek', label: 'DeepSeek', models: ['deepseek-chat', 'deepseek-coder'] },
    { value: 'zhipu', label: '智谱 GLM', models: ['glm-4', 'glm-4-flash', 'glm-4-plus'] },
    { value: 'qwen', label: '通义千问', models: ['qwen-max', 'qwen-plus', 'qwen-turbo'] },
    { value: 'anthropic', label: 'Anthropic', models: ['claude-3-5-sonnet', 'claude-3-opus', 'claude-3-haiku'] },
    { value: 'ollama', label: 'Ollama (本地)', models: ['llama3', 'mistral', 'qwen2', 'deepseek-r1'] },
  ]

  // 当前提供商的模型列表
  const currentProviderModels = computed(() => {
    const p = providers.find((p) => p.value === provider.value)
    return p ? p.models : []
  })

  // 获取完整的 LLM 配置对象（发送给后端）
  function getLLMConfig() {
    return {
      provider: provider.value,
      model_name: modelName.value,
      api_key: apiKey.value,
      base_url: baseUrl.value || null,
      temperature: temperature.value,
      max_tokens: maxTokens.value,
    }
  }

  // 持久化到 localStorage
  function save() {
    localStorage.setItem('llm_provider', provider.value)
    localStorage.setItem('llm_model', modelName.value)
    localStorage.setItem('llm_api_key', apiKey.value)
    localStorage.setItem('llm_base_url', baseUrl.value)
    localStorage.setItem('llm_temperature', String(temperature.value))
    localStorage.setItem('llm_max_tokens', String(maxTokens.value))
    localStorage.setItem('default_question_count', String(defaultQuestionCount.value))
    localStorage.setItem('default_language', defaultLanguage.value)
    localStorage.setItem('default_interview_type', defaultInterviewType.value)
  }

  // 切换提供商时重置模型
  function setProvider(val) {
    provider.value = val
    const p = providers.find((p) => p.value === val)
    if (p && p.models.length > 0) {
      modelName.value = p.models[0]
    }
    save()
  }

  return {
    provider,
    modelName,
    apiKey,
    baseUrl,
    temperature,
    maxTokens,
    defaultQuestionCount,
    defaultLanguage,
    defaultInterviewType,
    providers,
    currentProviderModels,
    getLLMConfig,
    save,
    setProvider,
  }
})
