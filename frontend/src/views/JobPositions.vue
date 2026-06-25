<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">职位管理</h1>
        <p class="text-sm text-on-surface-variant mt-1">管理和创建招聘岗位</p>
      </div>
      <button @click="showForm = true; editingJob = null" class="btn-primary flex items-center gap-2">
        <span class="material-symbols-outlined text-lg">add</span>
        新增职位
      </button>
    </div>

    <!-- 职位列表 -->
    <div v-if="loading" class="text-center py-12 text-on-surface-variant">
      <span class="material-symbols-outlined animate-spin text-3xl">progress_activity</span>
    </div>

    <div v-else-if="jobs.length === 0" class="glass-card p-12 text-center">
      <span class="material-symbols-outlined text-5xl text-on-surface-variant/30 mb-4 block">work_off</span>
      <p class="text-on-surface-variant">暂无职位，点击上方按钮创建</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="job in jobs" :key="job.id" class="glass-card p-5 hover:border-primary/30 transition-all group">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-base">{{ job.title }}</h3>
            <p class="text-xs text-on-surface-variant mt-0.5">{{ job.department || '未指定部门' }}</p>
          </div>
          <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="editJob(job)" class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-surface-container text-on-surface-variant">
              <span class="material-symbols-outlined text-sm">edit</span>
            </button>
            <button @click="deleteJob(job.id)" class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-error/10 text-on-surface-variant hover:text-error">
              <span class="material-symbols-outlined text-sm">delete</span>
            </button>
          </div>
        </div>
        <p class="text-sm text-on-surface-variant line-clamp-2 mb-3">{{ job.description || '暂无描述' }}</p>
        <div class="flex flex-wrap gap-1.5">
          <span v-for="skill in (job.skills_required || []).slice(0, 4)" :key="skill" class="badge badge-blue text-[10px]">{{ skill }}</span>
          <span v-if="(job.skills_required || []).length > 4" class="text-[10px] text-on-surface-variant">+{{ job.skills_required.length - 4 }}</span>
        </div>
        <div class="mt-3 pt-3 border-t border-outline-variant/20 flex items-center justify-between">
          <span class="text-[10px] font-mono text-on-surface-variant">{{ job.created_at?.slice(0, 10) || '' }}</span>
          <button @click="startInterviewWithJob(job)" class="text-xs text-secondary hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-sm">play_arrow</span>开始面试
          </button>
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showForm = false">
      <div class="glass-card-elevated w-full max-w-lg mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <h2 class="text-lg font-semibold">{{ editingJob ? '编辑职位' : '新增职位' }}</h2>

        <div>
          <label class="block text-sm font-medium mb-1">职位名称 *</label>
          <input v-model="form.title" placeholder="如：高级前端工程师" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">部门</label>
          <input v-model="form.department" placeholder="如：技术部" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">职位描述</label>
          <textarea v-model="form.description" rows="3" placeholder="描述岗位的核心职责和工作内容..." class="input-field resize-none"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">任职要求</label>
          <textarea v-model="form.requirements" rows="3" placeholder="学历、经验、技能等要求..." class="input-field resize-none"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">技能标签</label>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span v-for="(s, i) in form.skills_required" :key="i" class="badge badge-blue cursor-pointer text-[10px]" @click="form.skills_required.splice(i, 1)">
              {{ s }} ×
            </span>
          </div>
          <div class="flex gap-2">
            <input
              v-model="skillInput"
              placeholder="输入技能后回车"
              class="input-field flex-1 text-sm"
              @keyup.enter="addSkill"
            />
            <button @click="addSkill" class="btn-secondary text-sm">添加</button>
          </div>
        </div>

        <div class="flex gap-3 pt-2">
          <button @click="saveJob" :disabled="!form.title" class="btn-primary flex-1">
            {{ editingJob ? '保存修改' : '创建职位' }}
          </button>
          <button @click="showForm = false" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { jobsAPI } from '@/api'

const router = useRouter()
const jobs = ref([])
const loading = ref(true)
const showForm = ref(false)
const editingJob = ref(null)
const skillInput = ref('')

const form = ref({
  title: '',
  department: '',
  description: '',
  requirements: '',
  skills_required: [],
})

function addSkill() {
  const s = skillInput.value.trim()
  if (s && !form.value.skills_required.includes(s)) {
    form.value.skills_required.push(s)
  }
  skillInput.value = ''
}

function resetForm() {
  form.value = { title: '', department: '', description: '', requirements: '', skills_required: [] }
  skillInput.value = ''
}

function editJob(job) {
  editingJob.value = job
  form.value = {
    title: job.title || '',
    department: job.department || '',
    description: job.description || '',
    requirements: job.requirements || '',
    skills_required: [...(job.skills_required || [])],
  }
  showForm.value = true
}

async function saveJob() {
  try {
    if (editingJob.value) {
      await jobsAPI.update(editingJob.value.id, { ...form.value })
    } else {
      await jobsAPI.create({ ...form.value })
    }
    showForm.value = false
    resetForm()
    editingJob.value = null
    await loadJobs()
  } catch (e) {
    alert('操作失败: ' + e.message)
  }
}

async function deleteJob(id) {
  if (!confirm('确认删除此职位？')) return
  try {
    await jobsAPI.delete(id)
    await loadJobs()
  } catch (e) {
    alert('删除失败: ' + e.message)
  }
}

function startInterviewWithJob(job) {
  router.push({ path: '/interview', query: { job_id: job.id } })
}

async function loadJobs() {
  loading.value = true
  try {
    const res = await jobsAPI.list()
    jobs.value = res.data || []
  } catch {
    jobs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadJobs)
</script>
