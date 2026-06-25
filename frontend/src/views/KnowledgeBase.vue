<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">知识库</h1>
        <p class="text-sm text-on-surface-variant mt-1">
          RAG 增强检索的知识内容库 · <span class="badge badge-green text-[10px]">ChromaDB 向量索引</span>
        </p>
      </div>
      <div class="flex gap-2">
        <button @click="rebuildIndex" :disabled="indexing" class="btn-secondary text-sm flex items-center gap-1.5">
          <span class="material-symbols-outlined text-lg">{{ indexing ? 'progress_activity' : 'database' }}</span>
          {{ indexing ? '重建中...' : '重建索引' }}
        </button>
        <button @click="showForm = true; editingItem = null" class="btn-primary flex items-center gap-2">
          <span class="material-symbols-outlined text-lg">add</span>
          添加知识
        </button>
      </div>
    </div>

    <!-- RAG 搜索 -->
    <div class="glass-card p-4">
      <div class="flex gap-3">
        <div class="relative flex-1">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
          <input
            v-model="searchQuery"
            @keyup.enter="searchKnowledge"
            placeholder="语义搜索知识库..."
            class="input-field pl-10"
          />
        </div>
        <button @click="searchKnowledge" :disabled="searching" class="btn-primary flex items-center gap-2">
          <span class="material-symbols-outlined text-lg">{{ searching ? 'progress_activity' : 'search' }}</span>
          搜索
        </button>
      </div>
      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="mt-4 space-y-3">
        <p class="text-xs text-on-surface-variant">
          找到 {{ searchResults.length }} 条相关结果
          <button @click="searchResults = []; searchQuery = ''" class="text-primary ml-2 hover:underline">清除</button>
        </p>
        <div v-for="(r, i) in searchResults" :key="i" class="p-3 rounded-xl bg-surface-container">
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium">{{ r.title }}</span>
            <span class="text-[10px] font-mono text-tertiary">{{ (r.relevance * 100).toFixed(0) }}% 相关</span>
          </div>
          <p class="text-xs text-on-surface-variant line-clamp-2">{{ r.content }}</p>
        </div>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="filterCategory = cat.value; loadItems()"
        class="px-3 py-1.5 rounded-lg text-xs border transition-all"
        :class="filterCategory === cat.value ? 'border-primary bg-primary/10 text-primary' : 'border-outline-variant/30 text-on-surface-variant hover:border-outline'"
      >{{ cat.label }}</button>
    </div>

    <!-- 知识列表 -->
    <div v-if="loading" class="text-center py-12 text-on-surface-variant">
      <span class="material-symbols-outlined animate-spin text-3xl">progress_activity</span>
    </div>

    <div v-else-if="items.length === 0" class="glass-card p-12 text-center">
      <span class="material-symbols-outlined text-5xl text-on-surface-variant/30 mb-4 block">book_off</span>
      <p class="text-on-surface-variant">暂无知识条目</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="item in items" :key="item.id" class="glass-card p-5 hover:border-secondary/30 transition-all group">
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="badge" :class="categoryBadgeClass(item.category)">{{ categoryLabel(item.category) }}</span>
          </div>
          <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="editItem(item)" class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-surface-container text-on-surface-variant">
              <span class="material-symbols-outlined text-sm">edit</span>
            </button>
            <button @click="deleteItem(item.id)" class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-error/10 text-on-surface-variant hover:text-error">
              <span class="material-symbols-outlined text-sm">delete</span>
            </button>
          </div>
        </div>
        <h3 class="font-semibold text-base mb-2">{{ item.title }}</h3>
        <p class="text-sm text-on-surface-variant line-clamp-3">{{ item.content }}</p>
        <div class="flex flex-wrap gap-1 mt-3">
          <span v-for="tag in (item.tags || []).slice(0, 5)" :key="tag" class="text-[10px] text-on-surface-variant/60">#{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showForm = false">
      <div class="glass-card-elevated w-full max-w-lg mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <h2 class="text-lg font-semibold">{{ editingItem ? '编辑知识' : '添加知识' }}</h2>
        <div>
          <label class="block text-sm font-medium mb-1">标题 *</label>
          <input v-model="form.title" placeholder="知识标题" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">分类</label>
          <select v-model="form.category" class="input-field">
            <option value="company">公司信息</option>
            <option value="tech">技术知识</option>
            <option value="role">岗位要求</option>
            <option value="general">通用知识</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">内容 *</label>
          <textarea v-model="form.content" rows="6" placeholder="知识内容，会被 RAG 索引用于面试..." class="input-field resize-none"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">标签</label>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span v-for="(t, i) in form.tags" :key="i" class="badge badge-blue cursor-pointer text-[10px]" @click="form.tags.splice(i, 1)">{{ t }} ×</span>
          </div>
          <div class="flex gap-2">
            <input v-model="tagInput" placeholder="输入标签后回车" class="input-field flex-1 text-sm" @keyup.enter="addTag" />
            <button @click="addTag" class="btn-secondary text-sm">添加</button>
          </div>
        </div>
        <div class="flex gap-3 pt-2">
          <button @click="saveItem" :disabled="!form.title || !form.content" class="btn-primary flex-1">
            {{ editingItem ? '保存修改' : '添加知识' }}
          </button>
          <button @click="showForm = false" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { knowledgeAPI } from '@/api'

const items = ref([])
const loading = ref(true)
const showForm = ref(false)
const editingItem = ref(null)
const tagInput = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const indexing = ref(false)
const filterCategory = ref('')

const categories = [
  { value: '', label: '全部' },
  { value: 'company', label: '🏢 公司信息' },
  { value: 'tech', label: '💻 技术知识' },
  { value: 'role', label: '📋 岗位要求' },
  { value: 'general', label: '📖 通用知识' },
]

const form = ref({ title: '', content: '', category: 'general', tags: [] })

function addTag() {
  const t = tagInput.value.trim()
  if (t && !form.value.tags.includes(t)) form.value.tags.push(t)
  tagInput.value = ''
}

function categoryLabel(cat) {
  const map = { company: '公司信息', tech: '技术知识', role: '岗位要求', general: '通用知识' }
  return map[cat] || cat
}

function categoryBadgeClass(cat) {
  const map = { company: 'badge-blue', tech: 'badge-green', role: 'badge-amber', general: '' }
  return map[cat] || ''
}

function editItem(item) {
  editingItem.value = item
  form.value = {
    title: item.title || '',
    content: item.content || '',
    category: item.category || 'general',
    tags: [...(item.tags || [])],
  }
  showForm.value = true
}

async function saveItem() {
  try {
    if (editingItem.value) {
      await knowledgeAPI.update(editingItem.value.id, { ...form.value })
    } else {
      await knowledgeAPI.create({ ...form.value })
    }
    showForm.value = false
    editingItem.value = null
    resetForm()
    await loadItems()
  } catch (e) {
    alert('操作失败: ' + e.message)
  }
}

async function deleteItem(id) {
  if (!confirm('确认删除？此操作会同步移除 RAG 向量索引。')) return
  try {
    await knowledgeAPI.delete(id)
    await loadItems()
  } catch (e) {
    alert('删除失败: ' + e.message)
  }
}

async function searchKnowledge() {
  if (!searchQuery.value.trim()) return
  searching.value = true
  try {
    const res = await knowledgeAPI.search(searchQuery.value.trim(), 5)
    searchResults.value = res.data || []
  } catch (e) {
    alert('搜索失败: ' + e.message)
  } finally {
    searching.value = false
  }
}

async function rebuildIndex() {
  indexing.value = true
  try {
    const res = await knowledgeAPI.rebuildIndex()
    alert(`索引重建完成: ${res.data?.count || 0} 条`)
  } catch (e) {
    alert('重建失败: ' + e.message)
  } finally {
    indexing.value = false
  }
}

function resetForm() {
  form.value = { title: '', content: '', category: 'general', tags: [] }
  tagInput.value = ''
}

async function loadItems() {
  loading.value = true
  try {
    const res = await knowledgeAPI.list(filterCategory.value || undefined)
    items.value = res.data || []
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadItems)
</script>
