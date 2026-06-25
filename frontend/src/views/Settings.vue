<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">系统设置</h1>
        <p class="text-sm text-on-surface-variant mt-1">配置大模型和面试参数</p>
      </div>
      <button @click="saveSettings" class="btn-primary flex items-center gap-2">
        <span class="material-symbols-outlined text-lg">save</span>
        保存配置
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- LLM 模型配置 -->
      <div class="glass-card p-6 space-y-5">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-primary text-2xl">smart_toy</span>
          <div>
            <h2 class="text-lg font-semibold">大模型配置</h2>
            <p class="text-xs text-on-surface-variant">选择模型提供商和参数</p>
          </div>
        </div>

        <!-- 提供商选择 -->
        <div>
          <label class="block text-sm font-medium mb-2">模型提供商</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="p in settings.providers"
              :key="p.value"
              @click="settings.setProvider(p.value)"
              class="px-3 py-2.5 rounded-lg text-xs font-medium border transition-all text-center"
              :class="settings.provider === p.value
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-outline-variant/30 text-on-surface-variant hover:border-outline'"
            >
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- 模型选择 -->
        <div>
          <label class="block text-sm font-medium mb-2">模型名称</label>
          <select
            v-model="settings.modelName"
            @change="settings.save()"
            class="input-field"
          >
            <option
              v-for="m in settings.currentProviderModels"
              :key="m"
              :value="m"
            >{{ m }}</option>
          </select>
          <!-- 自定义模型名 -->
          <div class="mt-2 flex items-center gap-2">
            <input
              v-model="customModel"
              placeholder="或输入自定义模型名..."
              class="input-field flex-1 text-xs py-1.5"
              @blur="applyCustomModel"
              @keyup.enter="applyCustomModel"
            />
          </div>
        </div>

        <!-- API Key -->
        <div>
          <label class="block text-sm font-medium mb-2">
            API Key
            <span class="text-xs text-on-surface-variant ml-1">（仅存储在本地浏览器）</span>
          </label>
          <div class="relative">
            <input
              v-model="settings.apiKey"
              :type="showKey ? 'text' : 'password'"
              @change="settings.save()"
              placeholder="sk-..."
              class="input-field pr-10 font-mono text-sm"
            />
            <button
              @click="showKey = !showKey"
              class="absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface"
            >
              <span class="material-symbols-outlined text-lg">{{ showKey ? 'visibility_off' : 'visibility' }}</span>
            </button>
          </div>
        </div>

        <!-- 自定义 API 端点 -->
        <div>
          <label class="block text-sm font-medium mb-2">
            自定义 API 端点
            <span class="text-xs text-on-surface-variant ml-1">（可选，用于代理或兼容 API）</span>
          </label>
          <input
            v-model="settings.baseUrl"
            @change="settings.save()"
            placeholder="https://api.openai.com/v1"
            class="input-field font-mono text-sm"
          />
        </div>

        <!-- 参数调节 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">
              温度 ({{ settings.temperature }})
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              v-model.number="settings.temperature"
              @change="settings.save()"
              class="w-full accent-primary"
            />
            <div class="flex justify-between text-xs text-on-surface-variant mt-1">
              <span>精确</span>
              <span>创意</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">
              最大 Token ({{ settings.maxTokens }})
            </label>
            <input
              type="range"
              min="512"
              max="32768"
              step="512"
              v-model.number="settings.maxTokens"
              @change="settings.save()"
              class="w-full accent-primary"
            />
          </div>
        </div>
      </div>

      <!-- 面试默认配置 -->
      <div class="space-y-6">
        <div class="glass-card p-6 space-y-5">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-secondary text-2xl">tune</span>
            <div>
              <h2 class="text-lg font-semibold">面试默认参数</h2>
              <p class="text-xs text-on-surface-variant">新面试的默认设置</p>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">默认题目数量</label>
            <select v-model="settings.defaultQuestionCount" @change="settings.save()" class="input-field">
              <option :value="3">3 题（快速面试）</option>
              <option :value="5">5 题（标准面试）</option>
              <option :value="8">8 题（深度面试）</option>
              <option :value="10">10 题（全面面试）</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">面试语言</label>
            <div class="flex gap-3">
              <button
                v-for="lang in [{v:'zh',l:'中文'},{v:'en',l:'English'}]"
                :key="lang.v"
                @click="settings.defaultLanguage = lang.v; settings.save()"
                class="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium border transition-all"
                :class="settings.defaultLanguage === lang.v
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-outline-variant/30 text-on-surface-variant hover:border-outline'"
              >{{ lang.l }}</button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">面试类型</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="t in [{v:'technical',l:'技术面'},{v:'behavioral',l:'行为面'},{v:'mixed',l:'综合面'}]"
                :key="t.v"
                @click="settings.defaultInterviewType = t.v; settings.save()"
                class="px-3 py-2 rounded-lg text-xs font-medium border transition-all text-center"
                :class="settings.defaultInterviewType === t.v
                  ? 'border-secondary bg-secondary/10 text-secondary'
                  : 'border-outline-variant/30 text-on-surface-variant hover:border-outline'"
              >{{ t.l }}</button>
            </div>
          </div>
        </div>

        <!-- 连接状态 -->
        <div class="glass-card p-6 space-y-4">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-tertiary text-2xl">cloud</span>
            <div>
              <h2 class="text-lg font-semibold">系统状态</h2>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between py-2">
              <span class="text-sm text-on-surface-variant">后端 API</span>
              <span class="flex items-center gap-1.5 text-sm" :class="backendStatus === 'ok' ? 'text-tertiary' : 'text-error'">
                <span class="w-2 h-2 rounded-full" :class="backendStatus === 'ok' ? 'bg-tertiary' : 'bg-error'"></span>
                {{ backendStatus === 'ok' ? '已连接' : '未连接' }}
              </span>
            </div>
            <div class="flex items-center justify-between py-2">
              <span class="text-sm text-on-surface-variant">LLM API</span>
              <span class="flex items-center gap-1.5 text-sm" :class="settings.apiKey ? 'text-tertiary' : 'text-amber-400'">
                <span class="w-2 h-2 rounded-full" :class="settings.apiKey ? 'bg-tertiary' : 'bg-amber-400'"></span>
                {{ settings.apiKey ? '已配置' : '未配置 API Key' }}
              </span>
            </div>
            <button @click="checkHealth" class="btn-secondary w-full text-sm flex items-center justify-center gap-2">
              <span class="material-symbols-outlined text-lg">refresh</span>
              检测连接
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存提示 -->
    <transition name="fade">
      <div v-if="saved" class="fixed bottom-6 right-6 glass-card-elevated px-5 py-3 rounded-xl flex items-center gap-2 text-sm z-50">
        <span class="material-symbols-outlined text-tertiary">check_circle</span>
        设置已保存
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { healthAPI } from '@/api'

const settings = useSettingsStore()
const showKey = ref(false)
const customModel = ref('')
const saved = ref(false)
const backendStatus = ref('unknown')

function applyCustomModel() {
  if (customModel.value.trim()) {
    settings.modelName = customModel.value.trim()
    settings.save()
    customModel.value = ''
  }
}

function saveSettings() {
  settings.save()
  saved.value = true
  setTimeout(() => (saved.value = false), 2000)
}

async function checkHealth() {
  try {
    const res = await healthAPI.check()
    backendStatus.value = res.status || 'ok'
  } catch {
    backendStatus.value = 'error'
  }
}

onMounted(() => checkHealth())
</script>
