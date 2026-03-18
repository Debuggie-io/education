<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Notifications</h1>
      <Button
        v-if="unreadCount > 0"
        variant="subtle"
        label="Mark All as Read"
        @click="markAllAsRead"
      />
    </div>

    <!-- Stats -->
    <div class="flex items-center space-x-4">
      <Badge variant="subtle" theme="blue" :label="`${unreadCount} Unread`" />
      <Badge variant="subtle" theme="gray" :label="`${notifications.length} Total`" />
    </div>

    <!-- Loading State -->
    <div v-if="notificationsLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Notifications -->
    <div v-else-if="notifications.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <Bell class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Notifications</h3>
      <p class="text-gray-500">You're all caught up!</p>
    </div>

    <!-- Notifications List -->
    <div v-else class="space-y-2">
      <div
        v-for="notification in notifications"
        :key="notification.name"
        class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
        :class="{ 'border-l-4 border-blue-500': !notification.read }"
        @click="handleNotificationClick(notification)"
      >
        <div class="flex items-start space-x-4">
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
            :class="notification.read ? 'bg-gray-100' : 'bg-blue-100'"
          >
            <component
              :is="getNotificationIcon(notification.document_type)"
              class="w-5 h-5"
              :class="notification.read ? 'text-gray-500' : 'text-blue-600'"
            />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900" :class="{ 'font-semibold': !notification.read }">
              {{ notification.subject }}
            </p>
            <p class="text-sm text-gray-500">
              {{ notification.document_type }} • {{ getRelativeTime(notification.creation) }}
            </p>
          </div>
          <div class="flex items-center space-x-2">
            <Button
              v-if="!notification.read"
              variant="subtle"
              size="sm"
              icon="check"
              @click.stop="markAsRead(notification)"
            />
            <Button
              variant="subtle"
              size="sm"
              icon="trash-2"
              @click.stop="deleteNotification(notification)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Load More -->
    <div v-if="hasMore" class="text-center">
      <Button
        variant="subtle"
        label="Load More"
        @click="loadMore"
        :loading="loadingMore"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast, getRelativeTime } from '@/utils'
import {
  Bell,
  FileText,
  DollarSign,
  Calendar,
  GraduationCap,
  MessageSquare
} from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const notifications = ref([])
const notificationsLoading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const notificationsResource = createResource({
  url: 'education.education.api.get_student_notifications',
  params: {
    student: studentInfo.value?.name,
    limit: 20
  },
  onSuccess: (data) => {
    notifications.value = data || []
    notificationsLoading.value = false
    hasMore.value = data?.length >= 20
  },
  onError: () => {
    notificationsLoading.value = false
  }
})

const markAsReadResource = createResource({
  url: 'education.education.api.mark_notification_read',
  onSuccess: () => {
    createToast({
      title: 'Notification marked as read',
      icon: 'check',
      iconClasses: 'text-green-600'
    })
  }
})

const getNotificationIcon = (doctype) => {
  const icons = {
    'Sales Invoice': DollarSign,
    'Assessment Result': GraduationCap,
    'Course Schedule': Calendar,
    'Student Attendance': Calendar,
    'Comment': MessageSquare
  }
  return icons[doctype] || FileText
}

const handleNotificationClick = (notification) => {
  if (!notification.read) {
    markAsRead(notification)
  }
  // Could navigate to the related document here
}

const markAsRead = (notification) => {
  notification.read = true
  markAsReadResource.submit({ notification_id: notification.name })
}

const markAllAsRead = () => {
  notifications.value.forEach(n => {
    if (!n.read) {
      markAsRead(n)
    }
  })
  createToast({
    title: 'All notifications marked as read',
    icon: 'check',
    iconClasses: 'text-green-600'
  })
}

const deleteNotification = (notification) => {
  const index = notifications.value.indexOf(notification)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const loadMore = () => {
  loadingMore.value = true
  // Would implement pagination here
  setTimeout(() => {
    loadingMore.value = false
  }, 1000)
}

onMounted(() => {
  if (studentInfo.value?.name) {
    notificationsResource.fetch()
  } else {
    notificationsLoading.value = false
  }
})
</script>
