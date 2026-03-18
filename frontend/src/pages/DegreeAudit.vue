<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Degree Audit</h1>
      <Button
        variant="subtle"
        icon-left="printer"
        label="Print Audit"
        @click="printAudit"
      />
    </div>

    <!-- Loading State -->
    <div v-if="auditLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <div v-else class="space-y-6">
      <!-- Program Overview -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-lg font-semibold text-gray-900">{{ auditData?.program_name || auditData?.program }}</h2>
            <p class="text-gray-500">{{ auditData?.program }}</p>
          </div>
          <div class="text-right">
            <div class="flex items-center space-x-2">
              <span class="text-3xl font-bold" :class="completionColor">
                {{ auditData?.completion_percentage || 0 }}%
              </span>
              <span class="text-gray-500">Complete</span>
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div
            class="h-4 rounded-full transition-all duration-500"
            :class="auditData?.completion_percentage >= 100 ? 'bg-green-600' : 'bg-blue-600'"
            :style="{ width: (auditData?.completion_percentage || 0) + '%' }"
          ></div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-2xl font-bold text-green-600">{{ auditData?.completed_requirements || 0 }}</p>
            <p class="text-sm text-gray-500">Completed</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-orange-600">
              {{ (auditData?.total_requirements || 0) - (auditData?.completed_requirements || 0) }}
            </p>
            <p class="text-sm text-gray-500">Remaining</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">{{ auditData?.total_requirements || 0 }}</p>
            <p class="text-sm text-gray-500">Total Required</p>
          </div>
        </div>
      </div>

      <!-- Course Requirements -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b">
          <h2 class="text-lg font-semibold text-gray-900">Course Requirements</h2>
        </div>

        <!-- Filters -->
        <div class="px-6 py-3 bg-gray-50 border-b flex items-center space-x-4">
          <button
            @click="filter = 'all'"
            class="px-3 py-1 rounded-full text-sm transition-colors"
            :class="filter === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          >
            All
          </button>
          <button
            @click="filter = 'completed'"
            class="px-3 py-1 rounded-full text-sm transition-colors"
            :class="filter === 'completed' ? 'bg-green-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          >
            Completed
          </button>
          <button
            @click="filter = 'pending'"
            class="px-3 py-1 rounded-full text-sm transition-colors"
            :class="filter === 'pending' ? 'bg-orange-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          >
            Pending
          </button>
        </div>

        <!-- Requirements List -->
        <div class="divide-y">
          <div
            v-for="item in filteredItems"
            :key="item.course"
            class="px-6 py-4 flex items-center justify-between"
            :class="item.completed ? 'bg-green-50' : 'bg-white'"
          >
            <div class="flex items-center space-x-4">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center"
                :class="item.completed ? 'bg-green-100' : 'bg-gray-100'"
              >
                <CheckCircle
                  v-if="item.completed"
                  class="w-6 h-6 text-green-600"
                />
                <Circle
                  v-else
                  class="w-6 h-6 text-gray-400"
                />
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ item.course_name || item.course }}</p>
                <p class="text-sm text-gray-500">{{ item.course }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div v-if="item.completed" class="text-right">
                <p class="font-medium text-gray-900">{{ item.score }}</p>
                <Badge
                  variant="subtle"
                  :theme="getGradeColor(item.grade)"
                  :label="item.grade"
                />
              </div>
              <Badge
                variant="subtle"
                :theme="item.completed ? 'green' : 'orange'"
                :label="item.status"
              />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredItems.length === 0" class="px-6 py-12 text-center">
          <p class="text-gray-500">No courses match the selected filter.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { CheckCircle, Circle } from 'lucide-vue-next'

const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

const auditData = ref(null)
const auditLoading = ref(true)
const filter = ref('all')

const auditResource = createResource({
  url: 'education.education.api.get_degree_audit',
  params: {
    student: studentInfo.value?.name,
    program: currentProgram.value?.program
  },
  onSuccess: (data) => {
    auditData.value = data
    auditLoading.value = false
  },
  onError: () => {
    auditLoading.value = false
  }
})

const filteredItems = computed(() => {
  if (!auditData.value?.audit_items) return []
  
  return auditData.value.audit_items.filter(item => {
    if (filter.value === 'all') return true
    if (filter.value === 'completed') return item.completed
    if (filter.value === 'pending') return !item.completed
    return true
  })
})

const completionColor = computed(() => {
  const pct = auditData.value?.completion_percentage || 0
  if (pct >= 100) return 'text-green-600'
  if (pct >= 75) return 'text-blue-600'
  if (pct >= 50) return 'text-orange-600'
  return 'text-red-600'
})

const getGradeColor = (grade) => {
  if (!grade || grade === '-') return 'gray'
  const g = grade.toUpperCase()
  if (g === 'A' || g === 'A+') return 'green'
  if (g === 'B' || g === 'B+') return 'blue'
  if (g === 'C' || g === 'C+') return 'yellow'
  return 'orange'
}

const printAudit = () => {
  window.print()
}

onMounted(() => {
  if (studentInfo.value?.name) {
    auditResource.fetch()
  } else {
    auditLoading.value = false
  }
})
</script>
