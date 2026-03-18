<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Clubs & Organizations</h1>
      <FormControl
        type="text"
        v-model="searchQuery"
        placeholder="Search clubs..."
        class="w-64"
      />
    </div>

    <!-- Categories Filter -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="category in categories"
        :key="category"
        @click="selectedCategory = category"
        class="px-4 py-2 rounded-full text-sm transition-colors"
        :class="selectedCategory === category 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >
        {{ category }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="clubsLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Clubs -->
    <div v-else-if="filteredClubs.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <Users class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Clubs Found</h3>
      <p class="text-gray-500">
        {{ searchQuery ? 'No clubs match your search.' : 'No clubs are available at this time.' }}
      </p>
    </div>

    <!-- Clubs Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="club in filteredClubs"
        :key="club.name"
        class="bg-white rounded-lg shadow overflow-hidden hover:shadow-md transition-shadow"
      >
        <!-- Club Header -->
        <div class="h-32 bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
          <Avatar
            v-if="club.logo"
            :image="club.logo"
            size="3xl"
            shape="circle"
            class="border-4 border-white"
          />
          <div
            v-else
            class="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center"
          >
            <Users class="w-10 h-10 text-white" />
          </div>
        </div>

        <!-- Club Info -->
        <div class="p-6">
          <div class="flex items-start justify-between mb-2">
            <h3 class="font-semibold text-gray-900">{{ club.club_name }}</h3>
            <Badge
              v-if="club.category"
              variant="subtle"
              theme="blue"
              :label="club.category"
              size="sm"
            />
          </div>

          <p class="text-sm text-gray-600 mb-4 line-clamp-2">
            {{ club.description || 'No description available.' }}
          </p>

          <div class="space-y-2 text-sm">
            <div v-if="club.meeting_schedule" class="flex items-center text-gray-500">
              <Calendar class="w-4 h-4 mr-2" />
              {{ club.meeting_schedule }}
            </div>
            <div v-if="club.advisor" class="flex items-center text-gray-500">
              <User class="w-4 h-4 mr-2" />
              Advisor: {{ club.advisor }}
            </div>
          </div>

          <div class="mt-4 pt-4 border-t flex items-center justify-between">
            <Button
              variant="subtle"
              size="sm"
              label="Learn More"
              @click="showClubDetails(club)"
            />
            <Button
              variant="solid"
              size="sm"
              label="Join"
              @click="joinClub(club)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Club Details Dialog -->
    <Dialog
      v-model="showDetailsDialog"
      :options="{ size: 'lg', title: selectedClub?.club_name }"
    >
      <template #body-content>
        <div v-if="selectedClub" class="space-y-4">
          <p class="text-gray-600">{{ selectedClub.description }}</p>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500">Category</p>
              <p class="font-medium text-gray-900">{{ selectedClub.category || 'General' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Meeting Schedule</p>
              <p class="font-medium text-gray-900">{{ selectedClub.meeting_schedule || 'TBD' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Advisor</p>
              <p class="font-medium text-gray-900">{{ selectedClub.advisor || 'Not assigned' }}</p>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex space-x-2">
          <Button variant="subtle" label="Close" @click="showDetailsDialog = false" />
          <Button variant="solid" label="Join Club" @click="joinClub(selectedClub)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Avatar, Spinner, FormControl, Dialog } from 'frappe-ui'
import { createToast } from '@/utils'
import { Users, Calendar, User } from 'lucide-vue-next'

const clubs = ref([])
const clubsLoading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('All')
const showDetailsDialog = ref(false)
const selectedClub = ref(null)

const categories = computed(() => {
  const cats = new Set(['All'])
  clubs.value.forEach(club => {
    if (club.category) cats.add(club.category)
  })
  return Array.from(cats)
})

const filteredClubs = computed(() => {
  return clubs.value.filter(club => {
    const matchesSearch = !searchQuery.value ||
      club.club_name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      club.description?.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesCategory = selectedCategory.value === 'All' ||
      club.category === selectedCategory.value
    
    return matchesSearch && matchesCategory
  })
})

const clubsResource = createResource({
  url: 'education.education.api.get_clubs_and_organizations',
  onSuccess: (data) => {
    clubs.value = data || []
    clubsLoading.value = false
  },
  onError: () => {
    clubsLoading.value = false
  }
})

const showClubDetails = (club) => {
  selectedClub.value = club
  showDetailsDialog.value = true
}

const joinClub = (club) => {
  createToast({
    title: `Request to join ${club.club_name} submitted`,
    icon: 'check',
    iconClasses: 'text-green-600'
  })
  showDetailsDialog.value = false
}

onMounted(() => {
  clubsResource.fetch()
})
</script>
