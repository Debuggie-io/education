<template>
  <div class="p-6 space-y-6">
    <!-- Welcome Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">
          Welcome back, {{ studentInfo?.student_name || 'Student' }}
        </h1>
        <p class="text-gray-600 mt-1">
          {{ currentProgram?.program || 'No program enrolled' }} • {{ currentProgram?.academic_year || '' }}
        </p>
      </div>
      <Avatar
        v-if="studentInfo?.image"
        :image="studentInfo.image"
        size="xl"
        shape="circle"
      />
      <div
        v-else
        class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center"
      >
        <User class="w-8 h-8 text-blue-600" />
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        title="GPA"
        :value="dashboardStats?.gpa?.toFixed(2) || '0.00'"
        :subtitle="'/4.00'"
        icon="award"
        color="blue"
      />
      <StatsCard
        title="Attendance"
        :value="(dashboardStats?.attendance_percentage || 0) + '%'"
        subtitle="This semester"
        icon="check-circle"
        color="green"
      />
      <StatsCard
        title="Fee Balance"
        :value="dashboardStats?.fee_balance || 'KES 0.00'"
        subtitle="Outstanding"
        icon="credit-card"
        :color="parseFloat(dashboardStats?.fee_balance?.replace(/[^0-9.-]+/g, '') || 0) > 0 ? 'red' : 'green'"
      />
      <StatsCard
        title="Notifications"
        :value="dashboardStats?.unread_notifications || 0"
        subtitle="Unread"
        icon="bell"
        :color="(dashboardStats?.unread_notifications || 0) > 0 ? 'orange' : 'gray'"
      />
    </div>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Upcoming Classes -->
      <div class="lg:col-span-2 bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Upcoming Classes</h2>
          <router-link
            to="/academics/schedule"
            class="text-blue-600 text-sm hover:underline"
          >
            View All
          </router-link>
        </div>
        <div v-if="upcomingClassesLoading" class="text-center py-8">
          <Spinner class="w-6 h-6 mx-auto" />
        </div>
        <div v-else-if="upcomingClasses.length === 0" class="text-center py-8 text-gray-500">
          No upcoming classes scheduled
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="classItem in upcomingClasses"
            :key="classItem.name"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                <BookOpen class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ classItem.title || classItem.course }}</p>
                <p class="text-sm text-gray-500">{{ classItem.room }} • {{ classItem.instructor }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-medium text-gray-900">{{ formatTime(classItem.from_time) }}</p>
              <p class="text-sm text-gray-500">{{ formatDate(classItem.schedule_date) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Links -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div class="space-y-2">
          <QuickLink to="/finance/statement" icon="file-text" label="View Fee Statement" />
          <QuickLink to="/academics/grades" icon="bar-chart-2" label="Check Grades" />
          <QuickLink to="/academics/attendance" icon="user-check" label="View Attendance" />
          <QuickLink to="/support/leave" icon="calendar" label="Apply for Leave" />
          <QuickLink to="/graduation/clearance" icon="check-square" label="Check Clearance" />
          <QuickLink to="/profile" icon="user" label="Update Profile" />
        </div>
      </div>
    </div>

    <!-- Recent Notifications -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Recent Notifications</h2>
        <router-link
          to="/notifications"
          class="text-blue-600 text-sm hover:underline"
        >
          View All
        </router-link>
      </div>
      <div v-if="notificationsLoading" class="text-center py-4">
        <Spinner class="w-6 h-6 mx-auto" />
      </div>
      <div v-else-if="notifications.length === 0" class="text-center py-4 text-gray-500">
        No new notifications
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="notification in notifications.slice(0, 5)"
          :key="notification.name"
          class="flex items-start space-x-3 p-3 rounded-lg"
          :class="notification.read ? 'bg-gray-50' : 'bg-blue-50'"
        >
          <Bell class="w-5 h-5 text-gray-400 mt-0.5" />
          <div class="flex-1">
            <p class="font-medium text-gray-900">{{ notification.subject }}</p>
            <p class="text-sm text-gray-500">{{ formatDate(notification.creation) }}</p>
          </div>
          <Badge
            v-if="!notification.read"
            variant="subtle"
            theme="blue"
            size="sm"
            label="New"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { createResource, Avatar, Badge, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { User, BookOpen, Bell } from 'lucide-vue-next'

// Components
const StatsCard = {
  props: ['title', 'value', 'subtitle', 'icon', 'color'],
  template: `
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">{{ title }}</p>
          <div class="flex items-baseline space-x-1">
            <p class="text-2xl font-bold" :class="'text-' + color + '-600'">{{ value }}</p>
            <span v-if="subtitle" class="text-sm text-gray-500">{{ subtitle }}</span>
          </div>
        </div>
        <div :class="'w-12 h-12 rounded-full flex items-center justify-center bg-' + color + '-100'">
          <FeatherIcon :name="icon" :class="'w-6 h-6 text-' + color + '-600'" />
        </div>
      </div>
    </div>
  `
}

const QuickLink = {
  props: ['to', 'icon', 'label'],
  template: `
    <router-link :to="to" class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
      <FeatherIcon :name="icon" class="w-5 h-5 text-gray-500" />
      <span class="text-gray-700">{{ label }}</span>
    </router-link>
  `
}

import { FeatherIcon } from 'frappe-ui'

const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

// Dashboard Stats
const dashboardStats = ref({})
const dashboardStatsResource = createResource({
  url: 'education.education.api.get_student_dashboard_stats',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    dashboardStats.value = data
  }
})

// Upcoming Classes
const upcomingClasses = ref([])
const upcomingClassesLoading = ref(true)
const upcomingClassesResource = createResource({
  url: 'education.education.api.get_upcoming_classes',
  params: {
    student: studentInfo.value?.name,
    limit: 5
  },
  onSuccess: (data) => {
    upcomingClasses.value = data || []
    upcomingClassesLoading.value = false
  },
  onError: () => {
    upcomingClassesLoading.value = false
  }
})

// Notifications
const notifications = ref([])
const notificationsLoading = ref(true)
const notificationsResource = createResource({
  url: 'education.education.api.get_student_notifications',
  params: {
    student: studentInfo.value?.name,
    limit: 10
  },
  onSuccess: (data) => {
    notifications.value = data || []
    notificationsLoading.value = false
  },
  onError: () => {
    notificationsLoading.value = false
  }
})

onMounted(() => {
  if (studentInfo.value?.name) {
    dashboardStatsResource.fetch()
    upcomingClassesResource.fetch()
    notificationsResource.fetch()
  }
})

// Utility functions
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatTime = (time) => {
  if (!time) return ''
  const [hours, minutes] = time.split(':')
  const h = parseInt(hours)
  const ampm = h >= 12 ? 'PM' : 'AM'
  const hour = h % 12 || 12
  return `${hour}:${minutes} ${ampm}`
}
</script>
