<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">My Room</h1>
      <router-link v-if="!roomData?.allocated" to="/residence/apply">
        <Button variant="solid" icon-left="plus" label="Apply for Housing" />
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="roomLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Room Allocated -->
    <div v-else-if="!roomData?.allocated" class="bg-white rounded-lg shadow p-12 text-center">
      <Home class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Room Assigned</h3>
      <p class="text-gray-500 mb-4">{{ roomData?.message || 'You have not been assigned a room yet.' }}</p>
      <router-link to="/residence/apply">
        <Button variant="solid" label="Apply for Housing" />
      </router-link>
    </div>

    <!-- Room Details -->
    <div v-else class="space-y-6">
      <!-- Room Card -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-8">
          <div class="flex items-center justify-between">
            <div class="text-white">
              <p class="text-blue-100 text-sm">Room Number</p>
              <h2 class="text-3xl font-bold">{{ roomData?.allocation?.room }}</h2>
              <p class="text-blue-100 mt-2">{{ roomData?.allocation?.building }}</p>
            </div>
            <div class="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center">
              <Home class="w-10 h-10 text-white" />
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <p class="text-sm text-gray-500">Building</p>
              <p class="font-semibold text-gray-900">{{ roomData?.allocation?.building || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Floor</p>
              <p class="font-semibold text-gray-900">{{ roomData?.allocation?.floor || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Allocation Date</p>
              <p class="font-semibold text-gray-900">{{ formatDate(roomData?.allocation?.allocation_date) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Expiry Date</p>
              <p class="font-semibold text-gray-900">{{ formatDate(roomData?.allocation?.expiry_date) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <router-link
          to="/residence/maintenance"
          class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow flex items-center space-x-4"
        >
          <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
            <Wrench class="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-900">Maintenance Request</p>
            <p class="text-sm text-gray-500">Report an issue</p>
          </div>
        </router-link>

        <div
          class="bg-white rounded-lg shadow p-6 flex items-center space-x-4 cursor-pointer hover:shadow-md transition-shadow"
          @click="showRulesDialog = true"
        >
          <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <FileText class="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-900">Hostel Rules</p>
            <p class="text-sm text-gray-500">View guidelines</p>
          </div>
        </div>

        <div
          class="bg-white rounded-lg shadow p-6 flex items-center space-x-4 cursor-pointer hover:shadow-md transition-shadow"
          @click="showContactDialog = true"
        >
          <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <Phone class="w-6 h-6 text-green-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-900">Contact Warden</p>
            <p class="text-sm text-gray-500">Get help</p>
          </div>
        </div>
      </div>

      <!-- Amenities -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-4">Room Amenities</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="flex items-center space-x-2 text-gray-600">
            <Wifi class="w-5 h-5" />
            <span>Wi-Fi</span>
          </div>
          <div class="flex items-center space-x-2 text-gray-600">
            <Bed class="w-5 h-5" />
            <span>Bed & Mattress</span>
          </div>
          <div class="flex items-center space-x-2 text-gray-600">
            <BookOpen class="w-5 h-5" />
            <span>Study Desk</span>
          </div>
          <div class="flex items-center space-x-2 text-gray-600">
            <Lamp class="w-5 h-5" />
            <span>Reading Lamp</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Rules Dialog -->
    <Dialog
      v-model="showRulesDialog"
      :options="{ size: 'lg', title: 'Hostel Rules & Guidelines' }"
    >
      <template #body-content>
        <div class="space-y-4 text-gray-700">
          <div>
            <h4 class="font-semibold text-gray-900 mb-2">General Rules</h4>
            <ul class="list-disc list-inside space-y-1 text-sm">
              <li>Quiet hours are from 10 PM to 6 AM</li>
              <li>Visitors must register at the front desk</li>
              <li>No cooking in rooms</li>
              <li>Keep your room clean and tidy</li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold text-gray-900 mb-2">Safety</h4>
            <ul class="list-disc list-inside space-y-1 text-sm">
              <li>No candles or open flames</li>
              <li>Report any safety hazards immediately</li>
              <li>Know your emergency exits</li>
            </ul>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="subtle" label="Close" @click="showRulesDialog = false" />
      </template>
    </Dialog>

    <!-- Contact Dialog -->
    <Dialog
      v-model="showContactDialog"
      :options="{ size: 'md', title: 'Hostel Contacts' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <div class="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
            <Phone class="w-8 h-8 text-blue-600" />
            <div>
              <p class="font-semibold text-gray-900">Hostel Warden</p>
              <p class="text-gray-600">+254 xxx xxx xxx</p>
            </div>
          </div>
          <div class="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
            <AlertTriangle class="w-8 h-8 text-red-600" />
            <div>
              <p class="font-semibold text-gray-900">Emergency</p>
              <p class="text-gray-600">+254 xxx xxx xxx</p>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="subtle" label="Close" @click="showContactDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Spinner, Dialog } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import {
  Home,
  Wrench,
  FileText,
  Phone,
  Wifi,
  Bed,
  BookOpen,
  Lamp,
  AlertTriangle
} from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const roomData = ref(null)
const roomLoading = ref(true)
const showRulesDialog = ref(false)
const showContactDialog = ref(false)

const roomResource = createResource({
  url: 'education.education.api.get_student_room_allocation',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    roomData.value = data
    roomLoading.value = false
  },
  onError: () => {
    roomLoading.value = false
  }
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  if (studentInfo.value?.name) {
    roomResource.fetch()
  } else {
    roomLoading.value = false
  }
})
</script>
