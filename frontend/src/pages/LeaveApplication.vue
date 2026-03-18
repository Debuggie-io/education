<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Leave Application</h1>
      <router-link to="/academics/attendance">
        <Button variant="subtle" icon-left="arrow-left" label="Back to Attendance" />
      </router-link>
    </div>

    <!-- Leave Form -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="max-w-2xl mx-auto">
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Apply for Leave</h2>
          <p class="text-gray-500 text-sm">Submit a leave application for your classes.</p>
        </div>

        <form @submit.prevent="submitLeave" class="space-y-6">
          <!-- Student Info -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Student Name:</span>
                <span class="ml-2 font-medium text-gray-900">{{ studentInfo?.student_name }}</span>
              </div>
              <div>
                <span class="text-gray-500">Student ID:</span>
                <span class="ml-2 font-medium text-gray-900">{{ studentInfo?.name }}</span>
              </div>
            </div>
          </div>

          <!-- Leave Type -->
          <FormControl
            label="Leave Type"
            v-model="form.leaveType"
            type="select"
            :options="leaveTypeOptions"
          />

          <!-- Date Range -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl
              label="From Date"
              v-model="form.fromDate"
              type="date"
              required
            />
            <FormControl
              label="To Date"
              v-model="form.toDate"
              type="date"
              required
            />
          </div>

          <!-- Total Days (Calculated) -->
          <div class="bg-blue-50 rounded-lg p-4">
            <div class="flex items-center justify-between">
              <span class="text-blue-700">Total Days:</span>
              <span class="font-bold text-blue-900 text-xl">{{ totalDays }}</span>
            </div>
          </div>

          <!-- Reason -->
          <FormControl
            label="Reason for Leave"
            v-model="form.reason"
            type="textarea"
            placeholder="Please provide a detailed reason for your leave application..."
            required
          />

          <!-- Supporting Document -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Supporting Document (optional)
            </label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Paperclip class="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p class="text-sm text-gray-500">Drag and drop or click to upload</p>
              <p class="text-xs text-gray-400 mt-1">PDF, JPG, PNG up to 5MB</p>
            </div>
          </div>

          <!-- Emergency Contact -->
          <FormControl
            label="Emergency Contact Number"
            v-model="form.emergencyContact"
            type="text"
            placeholder="Phone number during leave"
          />

          <!-- Terms -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-start space-x-3">
              <AlertTriangle class="w-5 h-5 text-yellow-600 mt-0.5" />
              <div class="text-sm text-yellow-800">
                <p class="font-medium">Important Notice:</p>
                <ul class="mt-1 list-disc list-inside">
                  <li>Leave applications should be submitted at least 3 days in advance</li>
                  <li>Attendance marked as "Leave" may affect your overall attendance percentage</li>
                  <li>Approval is subject to review by the concerned authority</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Submit Buttons -->
          <div class="flex justify-end space-x-3">
            <Button
              type="button"
              variant="subtle"
              label="Clear"
              @click="clearForm"
            />
            <Button
              type="submit"
              variant="solid"
              label="Submit Application"
              :loading="submitting"
              :disabled="!form.fromDate || !form.toDate || !form.reason"
            />
          </div>
        </form>
      </div>
    </div>

    <!-- Previous Leave Applications -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Previous Applications</h2>
      
      <div class="text-center py-8 text-gray-500">
        <Calendar class="w-12 h-12 text-gray-300 mx-auto mb-2" />
        <p>No previous leave applications found.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, FormControl } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast } from '@/utils'
import { Paperclip, AlertTriangle, Calendar } from 'lucide-vue-next'

const router = useRouter()
const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

const submitting = ref(false)

const form = reactive({
  leaveType: 'Personal',
  fromDate: '',
  toDate: '',
  reason: '',
  emergencyContact: ''
})

const leaveTypeOptions = [
  { label: 'Personal Leave', value: 'Personal' },
  { label: 'Medical Leave', value: 'Medical' },
  { label: 'Family Emergency', value: 'Family' },
  { label: 'Academic Event', value: 'Academic' },
  { label: 'Other', value: 'Other' }
]

const totalDays = computed(() => {
  if (!form.fromDate || !form.toDate) return 0
  
  const from = new Date(form.fromDate)
  const to = new Date(form.toDate)
  const diff = Math.ceil((to - from) / (1000 * 60 * 60 * 24)) + 1
  
  return diff > 0 ? diff : 0
})

const leaveResource = createResource({
  url: 'education.education.api.apply_leave',
  onSuccess: () => {
    submitting.value = false
    createToast({
      title: 'Leave application submitted successfully',
      icon: 'check',
      iconClasses: 'text-green-600'
    })
    router.push('/academics/attendance')
  },
  onError: (error) => {
    submitting.value = false
    createToast({
      title: error.messages?.[0] || 'Failed to submit application',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const submitLeave = () => {
  submitting.value = true
  
  const leaveData = {
    student: studentInfo.value?.name,
    student_name: studentInfo.value?.student_name,
    from_date: form.fromDate,
    to_date: form.toDate,
    total_days: totalDays.value,
    reason: form.reason
  }
  
  leaveResource.submit({
    leave_data: leaveData,
    program_name: currentProgram.value?.program
  })
}

const clearForm = () => {
  form.leaveType = 'Personal'
  form.fromDate = ''
  form.toDate = ''
  form.reason = ''
  form.emergencyContact = ''
}
</script>
