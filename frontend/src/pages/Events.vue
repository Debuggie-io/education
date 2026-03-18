<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Campus Events</h1>
      <div class="flex items-center space-x-2">
        <Button
          :variant="viewMode === 'list' ? 'solid' : 'subtle'"
          size="sm"
          icon-left="list"
          @click="viewMode = 'list'"
        />
        <Button
          :variant="viewMode === 'calendar' ? 'solid' : 'subtle'"
          size="sm"
          icon-left="calendar"
          @click="viewMode = 'calendar'"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="eventsLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Events -->
    <div v-else-if="events.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <Calendar class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Upcoming Events</h3>
      <p class="text-gray-500">There are no scheduled events at this time.</p>
    </div>

    <!-- Events List View -->
    <div v-else-if="viewMode === 'list'" class="space-y-4">
      <!-- Featured Event -->
      <div
        v-if="featuredEvent"
        class="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow p-6 text-white"
      >
        <div class="flex items-start justify-between">
          <div>
            <Badge variant="solid" theme="white" label="Featured" size="sm" class="mb-2" />
            <h2 class="text-2xl font-bold">{{ featuredEvent.event_name }}</h2>
            <p class="text-white/80 mt-2">{{ featuredEvent.description }}</p>
            <div class="flex items-center space-x-4 mt-4">
              <div class="flex items-center">
                <Calendar class="w-4 h-4 mr-2" />
                {{ formatDate(featuredEvent.event_date) }}
              </div>
              <div class="flex items-center">
                <Clock class="w-4 h-4 mr-2" />
                {{ featuredEvent.event_time || 'TBD' }}
              </div>
              <div class="flex items-center">
                <MapPin class="w-4 h-4 mr-2" />
                {{ featuredEvent.venue || 'TBD' }}
              </div>
            </div>
          </div>
          <Button
            variant="solid"
            theme="white"
            label="Register"
            @click="registerForEvent(featuredEvent)"
          />
        </div>
      </div>

      <!-- Other Events -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="event in otherEvents"
          :key="event.name"
          class="bg-white rounded-lg shadow overflow-hidden hover:shadow-md transition-shadow"
        >
          <div class="h-2" :class="getCategoryColor(event.category)"></div>
          <div class="p-6">
            <div class="flex items-start justify-between mb-2">
              <Badge
                v-if="event.category"
                variant="subtle"
                :theme="getCategoryTheme(event.category)"
                :label="event.category"
                size="sm"
              />
              <span class="text-sm text-gray-500">{{ formatDate(event.event_date) }}</span>
            </div>

            <h3 class="font-semibold text-gray-900 mb-2">{{ event.event_name }}</h3>
            <p class="text-sm text-gray-600 line-clamp-2 mb-4">
              {{ event.description || 'No description available.' }}
            </p>

            <div class="space-y-2 text-sm">
              <div class="flex items-center text-gray-500">
                <Clock class="w-4 h-4 mr-2" />
                {{ event.event_time || 'Time TBD' }}
              </div>
              <div class="flex items-center text-gray-500">
                <MapPin class="w-4 h-4 mr-2" />
                {{ event.venue || 'Venue TBD' }}
              </div>
              <div v-if="event.organizer" class="flex items-center text-gray-500">
                <Users class="w-4 h-4 mr-2" />
                {{ event.organizer }}
              </div>
            </div>

            <div class="mt-4 pt-4 border-t">
              <Button
                variant="subtle"
                size="sm"
                label="View Details"
                class="w-full"
                @click="viewEventDetails(event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-else class="bg-white rounded-lg shadow p-6">
      <p class="text-center text-gray-500 py-12">
        Calendar view coming soon...
      </p>
    </div>

    <!-- Event Details Dialog -->
    <Dialog
      v-model="showEventDialog"
      :options="{ size: 'lg', title: selectedEvent?.event_name }"
    >
      <template #body-content>
        <div v-if="selectedEvent" class="space-y-4">
          <p class="text-gray-600">{{ selectedEvent.description }}</p>
          
          <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
            <div>
              <p class="text-sm text-gray-500">Date</p>
              <p class="font-medium text-gray-900">{{ formatDate(selectedEvent.event_date) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Time</p>
              <p class="font-medium text-gray-900">{{ selectedEvent.event_time || 'TBD' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Venue</p>
              <p class="font-medium text-gray-900">{{ selectedEvent.venue || 'TBD' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Organizer</p>
              <p class="font-medium text-gray-900">{{ selectedEvent.organizer || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex space-x-2">
          <Button variant="subtle" label="Close" @click="showEventDialog = false" />
          <Button variant="solid" label="Register" @click="registerForEvent(selectedEvent)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Spinner, Dialog } from 'frappe-ui'
import { createToast } from '@/utils'
import { Calendar, Clock, MapPin, Users } from 'lucide-vue-next'

const events = ref([])
const eventsLoading = ref(true)
const viewMode = ref('list')
const showEventDialog = ref(false)
const selectedEvent = ref(null)

const eventsResource = createResource({
  url: 'education.education.api.get_student_events',
  params: { limit: 20 },
  onSuccess: (data) => {
    events.value = data || []
    eventsLoading.value = false
  },
  onError: () => {
    eventsLoading.value = false
  }
})

const featuredEvent = computed(() => events.value[0])
const otherEvents = computed(() => events.value.slice(1))

const formatDate = (date) => {
  if (!date) return 'TBD'
  return new Date(date).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}

const getCategoryColor = (category) => {
  const colors = {
    'Academic': 'bg-blue-500',
    'Sports': 'bg-green-500',
    'Cultural': 'bg-purple-500',
    'Social': 'bg-pink-500',
    'Religious': 'bg-yellow-500'
  }
  return colors[category] || 'bg-gray-500'
}

const getCategoryTheme = (category) => {
  const themes = {
    'Academic': 'blue',
    'Sports': 'green',
    'Cultural': 'purple',
    'Social': 'pink',
    'Religious': 'yellow'
  }
  return themes[category] || 'gray'
}

const viewEventDetails = (event) => {
  selectedEvent.value = event
  showEventDialog.value = true
}

const registerForEvent = (event) => {
  createToast({
    title: `Registered for ${event.event_name}`,
    icon: 'check',
    iconClasses: 'text-green-600'
  })
  showEventDialog.value = false
}

onMounted(() => {
  eventsResource.fetch()
})
</script>
