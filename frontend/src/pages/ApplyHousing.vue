<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Apply for Housing</h1>
      <router-link to="/residence/room">
        <Button variant="subtle" icon-left="arrow-left" label="Back to My Room" />
      </router-link>
    </div>

    <!-- Application Form -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="max-w-2xl mx-auto">
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Housing Application Form</h2>
          <p class="text-gray-500 text-sm">Fill in the details below to apply for on-campus housing.</p>
        </div>

        <form @submit.prevent="submitApplication" class="space-y-6">
          <!-- Student Info (Read-only) -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="font-medium text-gray-900 mb-3">Student Information</h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Name:</span>
                <span class="ml-2 text-gray-900">{{ studentInfo?.student_name }}</span>
              </div>
              <div>
                <span class="text-gray-500">Student ID:</span>
                <span class="ml-2 text-gray-900">{{ studentInfo?.name }}</span>
              </div>
              <div>
                <span class="text-gray-500">Program:</span>
                <span class="ml-2 text-gray-900">{{ currentProgram?.program }}</span>
              </div>
              <div>
                <span class="text-gray-500">Gender:</span>
                <span class="ml-2 text-gray-900">{{ studentInfo?.gender }}</span>
              </div>
            </div>
          </div>

          <!-- Room Preferences -->
          <div>
            <h3 class="font-medium text-gray-900 mb-3">Room Preferences</h3>
            
            <div class="space-y-4">
              <FormControl
                label="Preferred Room Type"
                v-model="form.roomType"
                type="select"
                :options="roomTypeOptions"
                required
              />

              <FormControl
                label="Preferred Building"
                v-model="form.building"
                type="select"
                :options="buildingOptions"
              />

              <FormControl
                label="Floor Preference"
                v-model="form.floorPreference"
                type="select"
                :options="floorOptions"
              />
            </div>
          </div>

          <!-- Special Requirements -->
          <div>
            <h3 class="font-medium text-gray-900 mb-3">Special Requirements</h3>
            
            <div class="space-y-4">
              <div class="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="accessibility"
                  v-model="form.accessibilityNeeds"
                  class="rounded border-gray-300"
                />
                <label for="accessibility" class="text-sm text-gray-700">
                  I require accessibility accommodations
                </label>
              </div>

              <FormControl
                label="Additional Notes"
                v-model="form.additionalNotes"
                type="textarea"
                placeholder="Any special requests or medical conditions we should know about..."
              />
            </div>
          </div>

          <!-- Academic Year -->
          <FormControl
            label="Academic Year"
            v-model="form.academicYear"
            type="text"
            :value="currentProgram?.academic_year"
            disabled
          />

          <!-- Terms & Conditions -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-start space-x-3">
              <input
                type="checkbox"
                id="terms"
                v-model="form.acceptTerms"
                class="rounded border-gray-300 mt-1"
                required
              />
              <label for="terms" class="text-sm text-yellow-800">
                I have read and agree to the housing terms and conditions, including the hostel rules
                and regulations. I understand that room assignments are subject to availability.
              </label>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end space-x-3">
            <router-link to="/residence/room">
              <Button variant="subtle" label="Cancel" />
            </router-link>
            <Button
              type="submit"
              variant="solid"
              label="Submit Application"
              :loading="submitting"
              :disabled="!form.acceptTerms || !form.roomType"
            />
          </div>
        </form>
      </div>
    </div>

    <!-- Available Rooms Preview -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Available Rooms</h2>
      
      <div v-if="roomsLoading" class="flex justify-center py-8">
        <Spinner class="w-6 h-6" />
      </div>

      <div v-else-if="availableRooms.length === 0" class="text-center py-8 text-gray-500">
        No rooms currently available. Please check back later.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="room in availableRooms.slice(0, 6)"
          :key="room.name"
          class="border rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-gray-900">{{ room.room_number }}</h3>
            <Badge variant="subtle" theme="green" label="Available" />
          </div>
          <p class="text-sm text-gray-500">{{ room.building }} - Floor {{ room.floor }}</p>
          <p class="text-sm text-gray-500">{{ room.room_type }} • Capacity: {{ room.capacity }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, FormControl, Badge, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast } from '@/utils'

const router = useRouter()
const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

const submitting = ref(false)
const availableRooms = ref([])
const roomsLoading = ref(true)

const form = reactive({
  roomType: '',
  building: '',
  floorPreference: '',
  accessibilityNeeds: false,
  additionalNotes: '',
  academicYear: currentProgram.value?.academic_year || '',
  acceptTerms: false
})

const roomTypeOptions = [
  { label: 'Single Room', value: 'single' },
  { label: 'Double Room', value: 'double' },
  { label: 'Triple Room', value: 'triple' },
  { label: 'No Preference', value: 'any' }
]

const buildingOptions = [
  { label: 'No Preference', value: '' },
  { label: 'Building A', value: 'Building A' },
  { label: 'Building B', value: 'Building B' },
  { label: 'Building C', value: 'Building C' }
]

const floorOptions = [
  { label: 'No Preference', value: '' },
  { label: 'Ground Floor', value: 'ground' },
  { label: 'First Floor', value: '1' },
  { label: 'Second Floor', value: '2' },
  { label: 'Third Floor', value: '3' }
]

// Fetch available rooms
const roomsResource = createResource({
  url: 'education.education.api.get_available_rooms',
  onSuccess: (data) => {
    availableRooms.value = data || []
    roomsLoading.value = false
  },
  onError: () => {
    roomsLoading.value = false
  }
})

// Submit application
const submitResource = createResource({
  url: 'education.education.api.apply_for_housing',
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
      title: error.message || 'Failed to submit application',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const submitApplication = () => {
  submitting.value = true
  submitResource.submit({
    student: studentInfo.value?.name,
    room_preference: form.roomType,
    academic_year: form.academicYear
  })
}

onMounted(() => {
  roomsResource.fetch()
})
</script>
