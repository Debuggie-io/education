<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Clearance Status</h1>
      <Button
        variant="solid"
        icon-left="download"
        label="Download Clearance Form"
        :disabled="!clearanceData?.overall_cleared"
        @click="downloadClearanceForm"
      />
    </div>

    <!-- Loading State -->
    <div v-if="clearanceLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <div v-else class="space-y-6">
      <!-- Overall Progress -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Overall Clearance Progress</h2>
          <Badge
            variant="subtle"
            :theme="clearanceData?.overall_cleared ? 'green' : 'orange'"
            :label="clearanceData?.overall_cleared ? 'Fully Cleared' : 'In Progress'"
          />
        </div>

        <div class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">
              {{ clearanceData?.cleared_count || 0 }} of {{ clearanceData?.total_count || 0 }} departments cleared
            </span>
            <span class="font-semibold text-gray-900">{{ clearanceData?.overall_progress || 0 }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-4">
            <div
              class="h-4 rounded-full transition-all duration-500"
              :class="clearanceData?.overall_cleared ? 'bg-green-600' : 'bg-blue-600'"
              :style="{ width: (clearanceData?.overall_progress || 0) + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Department Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="dept in clearanceData?.departments"
          :key="dept.department"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <div
            class="h-2"
            :class="dept.cleared ? 'bg-green-500' : 'bg-orange-500'"
          ></div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div
                  class="w-12 h-12 rounded-full flex items-center justify-center"
                  :class="dept.cleared ? 'bg-green-100' : 'bg-orange-100'"
                >
                  <component
                    :is="getDepartmentIcon(dept.department)"
                    class="w-6 h-6"
                    :class="dept.cleared ? 'text-green-600' : 'text-orange-600'"
                  />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900">{{ dept.department }}</h3>
                  <Badge
                    variant="subtle"
                    :theme="dept.cleared ? 'green' : 'orange'"
                    :label="dept.cleared ? 'Cleared' : 'Pending'"
                    size="sm"
                  />
                </div>
              </div>
            </div>

            <p class="text-sm text-gray-600 mb-4">{{ dept.details }}</p>

            <div v-if="!dept.cleared && dept.pending_items > 0" class="bg-orange-50 rounded-lg p-3">
              <p class="text-sm text-orange-800">
                <strong>{{ dept.pending_items }}</strong> pending item(s) to resolve
              </p>
            </div>

            <div v-if="dept.cleared" class="flex items-center text-green-600">
              <CheckCircle class="w-5 h-5 mr-2" />
              <span class="text-sm font-medium">All requirements met</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="bg-blue-50 rounded-lg p-6">
        <h3 class="font-semibold text-blue-900 mb-2">Clearance Instructions</h3>
        <ul class="list-disc list-inside text-blue-800 space-y-2 text-sm">
          <li>Visit each department to complete your clearance process</li>
          <li>Ensure all outstanding fees are paid before requesting finance clearance</li>
          <li>Return all library books and clear any library fines</li>
          <li>Return hostel keys and complete room inspection</li>
          <li>Once all departments are cleared, download your clearance form</li>
        </ul>
      </div>

      <!-- Contact Info -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-4">Need Help?</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex items-center space-x-3">
            <Phone class="w-5 h-5 text-gray-400" />
            <div>
              <p class="text-sm text-gray-500">Registrar's Office</p>
              <p class="font-medium text-gray-900">+254 xxx xxx xxx</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <Mail class="w-5 h-5 text-gray-400" />
            <div>
              <p class="text-sm text-gray-500">Email</p>
              <p class="font-medium text-gray-900">registrar@ueab.ac.ke</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import {
  CheckCircle,
  DollarSign,
  BookOpen,
  Home,
  GraduationCap,
  Users,
  Phone,
  Mail
} from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const clearanceData = ref(null)
const clearanceLoading = ref(true)

const clearanceResource = createResource({
  url: 'education.education.api.get_clearance_status',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    clearanceData.value = data
    clearanceLoading.value = false
  },
  onError: () => {
    clearanceLoading.value = false
  }
})

const getDepartmentIcon = (department) => {
  const icons = {
    'Finance': DollarSign,
    'Library': BookOpen,
    'Hostel': Home,
    'Academic': GraduationCap,
    'Student Affairs': Users
  }
  return icons[department] || CheckCircle
}

const downloadClearanceForm = () => {
  // TODO: Implement clearance form download
  alert('Clearance form download will be implemented')
}

onMounted(() => {
  if (studentInfo.value?.name) {
    clearanceResource.fetch()
  } else {
    clearanceLoading.value = false
  }
})
</script>
