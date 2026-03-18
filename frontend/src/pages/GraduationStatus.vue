<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Graduation Status</h1>
      <Badge
        variant="subtle"
        :theme="graduationStatus?.eligible ? 'green' : 'orange'"
        :label="graduationStatus?.status || 'Loading...'"
      />
    </div>

    <!-- Loading State -->
    <div v-if="statusLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <div v-else class="space-y-6">
      <!-- Progress Overview -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Program Completion Progress</h2>
        <div class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">Overall Progress</span>
            <span class="font-semibold text-gray-900">{{ graduationStatus?.completion_percentage || 0 }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-4">
            <div
              class="h-4 rounded-full transition-all duration-500"
              :class="graduationStatus?.completion_percentage >= 100 ? 'bg-green-600' : 'bg-blue-600'"
              :style="{ width: (graduationStatus?.completion_percentage || 0) + '%' }"
            ></div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div class="bg-blue-50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-blue-700">{{ graduationStatus?.completed_courses || 0 }}</p>
            <p class="text-sm text-blue-600">Courses Completed</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-gray-700">{{ graduationStatus?.total_required_courses || 0 }}</p>
            <p class="text-sm text-gray-600">Total Required</p>
          </div>
          <div class="bg-orange-50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-orange-700">
              {{ (graduationStatus?.total_required_courses || 0) - (graduationStatus?.completed_courses || 0) }}
            </p>
            <p class="text-sm text-orange-600">Remaining</p>
          </div>
        </div>
      </div>

      <!-- Eligibility Status -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Graduation Eligibility</h2>
        
        <div v-if="graduationStatus?.eligible" class="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <CheckCircle class="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h3 class="text-xl font-semibold text-green-800 mb-2">Congratulations!</h3>
          <p class="text-green-700">
            You have completed all program requirements and are eligible for graduation.
          </p>
          <div class="mt-4 flex justify-center space-x-4">
            <router-link to="/graduation/clearance">
              <Button variant="solid" label="Complete Clearance" />
            </router-link>
            <router-link to="/academics/transcripts">
              <Button variant="subtle" label="Request Transcript" />
            </router-link>
          </div>
        </div>

        <div v-else class="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <div class="flex items-start space-x-4">
            <AlertTriangle class="w-8 h-8 text-orange-600 flex-shrink-0" />
            <div>
              <h3 class="text-lg font-semibold text-orange-800 mb-2">Not Yet Eligible</h3>
              <p class="text-orange-700 mb-4">
                You have not yet completed all requirements for graduation.
                Please review your degree audit for pending requirements.
              </p>
              <router-link to="/graduation/audit">
                <Button variant="outline" label="View Degree Audit" />
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Program Information -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Program Information</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p class="text-sm text-gray-500">Program</p>
            <p class="font-medium text-gray-900">{{ graduationStatus?.program || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Student ID</p>
            <p class="font-medium text-gray-900">{{ graduationStatus?.student || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <!-- Quick Links -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <router-link
          to="/graduation/audit"
          class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow flex items-center space-x-4"
        >
          <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <ClipboardList class="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-900">Degree Audit</p>
            <p class="text-sm text-gray-500">Review requirements</p>
          </div>
        </router-link>

        <router-link
          to="/graduation/clearance"
          class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow flex items-center space-x-4"
        >
          <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <CheckSquare class="w-6 h-6 text-green-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-900">Clearance Status</p>
            <p class="text-sm text-gray-500">Check clearance</p>
          </div>
        </router-link>

        <router-link
          to="/academics/transcripts"
          class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow flex items-center space-x-4"
        >
          <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
            <FileText class="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-900">Transcript</p>
            <p class="text-sm text-gray-500">Request official copy</p>
          </div>
        </router-link>
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
  AlertTriangle,
  ClipboardList,
  CheckSquare,
  FileText
} from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const graduationStatus = ref(null)
const statusLoading = ref(true)

const statusResource = createResource({
  url: 'education.education.api.get_graduation_status',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    graduationStatus.value = data
    statusLoading.value = false
  },
  onError: () => {
    statusLoading.value = false
  }
})

onMounted(() => {
  if (studentInfo.value?.name) {
    statusResource.fetch()
  } else {
    statusLoading.value = false
  }
})
</script>
