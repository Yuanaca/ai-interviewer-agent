<template>
  <div class="min-h-screen bg-background text-on-surface">
    <!-- 顶部导航 -->
    <nav class="sticky top-0 z-50 border-b" style="background: rgba(10, 14, 26, 0.85); backdrop-filter: blur(16px); border-color: rgba(125, 211, 252, 0.06);">
      <div class="max-w-[1440px] mx-auto px-6 flex items-center justify-between h-16">
        <!-- 左侧 Logo -->
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background: rgba(125, 211, 252, 0.2); border: 1px solid rgba(125, 211, 252, 0.3);">
            <span class="material-symbols-outlined text-white text-xl">psychology</span>
          </div>
          <div>
            <h1 class="text-lg font-bold tracking-tight">Interview<span class="text-secondary">Intelligence</span></h1>
          </div>
        </div>

        <!-- 中间导航 -->
        <div class="hidden md:flex items-center gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            :class="$route.path === item.path
              ? 'text-primary bg-primary/8 border-r-2 border-primary'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'"
          >
            <span class="material-symbols-outlined text-lg">{{ item.icon }}</span>
            {{ item.label }}
          </router-link>
        </div>

        <!-- 右侧 -->
        <div class="flex items-center gap-3">
          <router-link to="/settings" class="w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-all">
            <span class="material-symbols-outlined">settings</span>
          </router-link>
        </div>
      </div>

      <!-- 移动端底部导航 -->
      <div class="md:hidden flex items-center justify-around py-2 border-t border-outline-variant/20">
        <router-link
          v-for="item in navItems.slice(0, 5)"
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center gap-1 px-3 py-1 text-xs transition-colors"
          :class="$route.path === item.path ? 'text-primary' : 'text-on-surface-variant'"
        >
          <span class="material-symbols-outlined text-xl">{{ item.icon }}</span>
          <span>{{ item.mobileLabel || item.label }}</span>
        </router-link>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="max-w-[1440px] mx-auto px-4 md:px-6 py-6">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const navItems = ref([
  { path: '/', icon: 'dashboard', label: '仪表盘', mobileLabel: '首页' },
  { path: '/interview', icon: 'videocam', label: '面试室', mobileLabel: '面试' },
  { path: '/jobs', icon: 'work', label: '职位管理', mobileLabel: '职位' },
  { path: '/knowledge', icon: 'book', label: '知识库', mobileLabel: '知识' },
  { path: '/reports', icon: 'assessment', label: '报告', mobileLabel: '报告' },
  { path: '/settings', icon: 'settings', label: '设置', mobileLabel: '设置' },
])
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
