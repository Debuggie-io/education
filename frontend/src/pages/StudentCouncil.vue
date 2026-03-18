<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <h1 class="text-2xl font-semibold text-gray-900">Student Council</h1>

    <!-- Council Overview -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold">Student Government Association</h2>
          <p class="text-blue-100 mt-1">Representing student voices since establishment</p>
        </div>
        <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
          <Users class="w-8 h-8 text-white" />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="councilLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Council -->
    <div v-else-if="councilMembers.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <Users class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Council Information</h3>
      <p class="text-gray-500">Student council information is not yet available.</p>
    </div>

    <!-- Council Members -->
    <div v-else>
      <!-- Executive Board -->
      <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
        <div class="px-6 py-4 border-b">
          <h2 class="text-lg font-semibold text-gray-900">Executive Board</h2>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div
              v-for="member in executiveMembers"
              :key="member.name"
              class="text-center"
            >
              <Avatar
                v-if="member.photo"
                :image="member.photo"
                size="3xl"
                shape="circle"
                class="mx-auto mb-3"
              />
              <div
                v-else
                class="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-3"
              >
                <User class="w-12 h-12 text-blue-600" />
              </div>
              <h3 class="font-semibold text-gray-900">{{ member.student_name }}</h3>
              <p class="text-blue-600 font-medium">{{ member.position }}</p>
              <p v-if="member.student_email_id" class="text-sm text-gray-500 mt-1">
                {{ member.student_email_id }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Other Members -->
      <div v-if="otherMembers.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b">
          <h2 class="text-lg font-semibold text-gray-900">Council Members</h2>
        </div>
        <div class="divide-y">
          <div
            v-for="member in otherMembers"
            :key="member.name"
            class="px-6 py-4 flex items-center space-x-4"
          >
            <Avatar
              v-if="member.photo"
              :image="member.photo"
              size="lg"
              shape="circle"
            />
            <div
              v-else
              class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center"
            >
              <User class="w-6 h-6 text-gray-600" />
            </div>
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ member.student_name }}</p>
              <p class="text-sm text-gray-500">{{ member.position }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact & Links -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-4">Contact Student Council</h3>
        <div class="space-y-3">
          <div class="flex items-center space-x-3">
            <Mail class="w-5 h-5 text-gray-400" />
            <span class="text-gray-600">sga@ueab.ac.ke</span>
          </div>
          <div class="flex items-center space-x-3">
            <MapPin class="w-5 h-5 text-gray-400" />
            <span class="text-gray-600">Student Center, Room 101</span>
          </div>
          <div class="flex items-center space-x-3">
            <Clock class="w-5 h-5 text-gray-400" />
            <span class="text-gray-600">Office Hours: Mon-Fri 9AM-4PM</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-4">Get Involved</h3>
        <div class="space-y-2">
          <router-link
            to="/governance/clubs"
            class="flex items-center space-x-2 text-blue-600 hover:underline"
          >
            <ArrowRight class="w-4 h-4" />
            <span>Join a Club</span>
          </router-link>
          <router-link
            to="/governance/events"
            class="flex items-center space-x-2 text-blue-600 hover:underline"
          >
            <ArrowRight class="w-4 h-4" />
            <span>Upcoming Events</span>
          </router-link>
          <router-link
            to="/governance/feedback"
            class="flex items-center space-x-2 text-blue-600 hover:underline"
          >
            <ArrowRight class="w-4 h-4" />
            <span>Submit Feedback</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Avatar, Spinner } from 'frappe-ui'
import { Users, User, Mail, MapPin, Clock, ArrowRight } from 'lucide-vue-next'

const councilMembers = ref([])
const councilLoading = ref(true)

const councilResource = createResource({
  url: 'education.education.api.get_student_council',
  onSuccess: (data) => {
    councilMembers.value = data || []
    councilLoading.value = false
  },
  onError: () => {
    councilLoading.value = false
  }
})

const executivePositions = ['President', 'Vice President', 'Secretary', 'Treasurer']

const executiveMembers = computed(() => {
  return councilMembers.value.filter(m =>
    executivePositions.some(p => m.position?.toLowerCase().includes(p.toLowerCase()))
  )
})

const otherMembers = computed(() => {
  return councilMembers.value.filter(m =>
    !executivePositions.some(p => m.position?.toLowerCase().includes(p.toLowerCase()))
  )
})

onMounted(() => {
  councilResource.fetch()
})
</script>
