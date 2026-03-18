<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Maintenance Request</h1>
      <router-link to="/residence/room">
        <Button variant="subtle" icon-left="arrow-left" label="Back to My Room" />
      </router-link>
    </div>

    <!-- Request Form -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="max-w-2xl mx-auto">
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Submit a Maintenance Request</h2>
          <p class="text-gray-500 text-sm">Report any issues with your room or building facilities.</p>
        </div>

        <form @submit.prevent="submitRequest" class="space-y-6">
          <!-- Room Info -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="font-medium text-gray-900 mb-2">Room Information</h3>
            <p class="text-gray-600">{{ roomInfo }}</p>
          </div>

          <!-- Issue Type -->
          <FormControl
            label="Issue Type"
            v-model="form.issueType"
            type="select"
            :options="issueTypeOptions"
            required
          />

          <!-- Priority -->
          <FormControl
            label="Priority"
            v-model="form.priority"
            type="select"
            :options="priorityOptions"
            required
          />

          <!-- Description -->
          <FormControl
            label="Description"
            v-model="form.description"
            type="textarea"
            placeholder="Please describe the issue in detail..."
            required
          />

          <!-- Photo Upload (optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Attach Photo (optional)
            </label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload class="w-10 h-10 text-gray-400 mx-auto mb-2" />
              <p class="text-sm text-gray-500">Drag and drop or click to upload</p>
              <p class="text-xs text-gray-400 mt-1">PNG, JPG up to 5MB</p>
            </div>
          </div>

          <!-- Preferred Time -->
          <FormControl
            label="Preferred Service Time"
            v-model="form.preferredTime"
            type="select"
            :options="timeOptions"
          />

          <!-- Contact Info -->
          <FormControl
            label="Contact Number"
            v-model="form.contactNumber"
            type="text"
            :placeholder="studentInfo?.student_mobile_number || 'Enter your phone number'"
          />

          <!-- Submit Button -->
          <div class="flex justify-end space-x-3">
            <router-link to="/residence/room">
              <Button variant="subtle" label="Cancel" />
            </router-link>
            <Button
              type="submit"
              variant="solid"
              label="Submit Request"
              :loading="submitting"
              :disabled="!form.issueType || !form.description"
            />
          </div>
        </form>
      </div>
    </div>

    <!-- Previous Requests -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Your Previous Requests</h2>

      <div class="text-center py-8 text-gray-500">
        <Wrench class="w-12 h-12 text-gray-300 mx-auto mb-2" />
        <p>No previous maintenance requests found.</p>
      </div>

      <!-- Would show a list of previous requests here -->
    </div>

    <!-- Emergency Contact -->
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center space-x-3">
        <AlertTriangle class="w-6 h-6 text-red-600" />
        <div>
          <p class="font-semibold text-red-800">For Emergencies</p>
          <p class="text-sm text-red-700">
            If this is an emergency (fire, flooding, security issue), please call the emergency line immediately: 
            <strong>+254 xxx xxx xxx</strong>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, FormControl } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast } from '@/utils'
import { Upload, Wrench, AlertTriangle } from 'lucide-vue-next'

const router = useRouter()
const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const submitting = ref(false)
const roomInfo = ref('Loading...')

const form = reactive({
  issueType: '',
  priority: 'Medium',
  description: '',
  preferredTime: '',
  contactNumber: ''
})

const issueTypeOptions = [
  { label: 'Select issue type', value: '' },
  { label: 'Electrical Issue', value: 'Electrical' },
  { label: 'Plumbing Issue', value: 'Plumbing' },
  { label: 'Furniture Repair', value: 'Furniture' },
  { label: 'Air Conditioning/Heating', value: 'HVAC' },
  { label: 'Door/Lock Issue', value: 'Door/Lock' },
  { label: 'Window Issue', value: 'Window' },
  { label: 'Pest Control', value: 'Pest' },
  { label: 'Cleaning', value: 'Cleaning' },
  { label: 'Other', value: 'Other' }
]

const priorityOptions = [
  { label: 'Low - Can wait', value: 'Low' },
  { label: 'Medium - Needs attention soon', value: 'Medium' },
  { label: 'High - Urgent issue', value: 'High' }
]

const timeOptions = [
  { label: 'Any time', value: '' },
  { label: 'Morning (8AM - 12PM)', value: 'Morning' },
  { label: 'Afternoon (12PM - 5PM)', value: 'Afternoon' },
  { label: 'Evening (5PM - 8PM)', value: 'Evening' }
]

// Fetch room allocation
const roomResource = createResource({
  url: 'education.education.api.get_student_room_allocation',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    if (data?.allocated && data?.allocation) {
      roomInfo.value = `Room ${data.allocation.room} - ${data.allocation.building}`
    } else {
      roomInfo.value = 'No room assigned'
    }
  },
  onError: () => {
    roomInfo.value = 'Unable to fetch room info'
  }
})

// Submit request
const submitResource = createResource({
  url: 'education.education.api.submit_maintenance_request',
  onSuccess: (data) => {
    submitting.value = false
    if (data.success) {
      createToast({
        title: data.message,
        icon: 'check',
        iconClasses: 'text-green-600'
      })
      router.push('/residence/room')
    } else {
      createToast({
        title: data.message,
        icon: 'x',
        iconClasses: 'text-red-600'
      })
    }
  },
  onError: (error) => {
    submitting.value = false
    createToast({
      title: error.message || 'Failed to submit request',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const submitRequest = () => {
  submitting.value = true
  submitResource.submit({
    student: studentInfo.value?.name,
    room: roomInfo.value,
    issue_type: form.issueType,
    description: form.description,
    priority: form.priority
  })
}

onMounted(() => {
  if (studentInfo.value?.name) {
    roomResource.fetch()
  }
  form.contactNumber = studentInfo.value?.student_mobile_number || ''
})
</script>
