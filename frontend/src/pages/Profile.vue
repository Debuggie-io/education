<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">My Profile</h1>
      <Button
        variant="solid"
        icon-left="edit"
        label="Edit Profile"
        @click="showEditDialog = true"
      />
    </div>

    <!-- Profile Card -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-8">
        <div class="flex items-center space-x-6">
          <div class="relative">
            <Avatar
              v-if="studentInfo?.image"
              :image="studentInfo.image"
              size="3xl"
              shape="circle"
              class="border-4 border-white"
            />
            <div
              v-else
              class="w-24 h-24 rounded-full bg-white flex items-center justify-center"
            >
              <User class="w-12 h-12 text-blue-600" />
            </div>
            <button
              @click="showPhotoUpload = true"
              class="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-white shadow flex items-center justify-center hover:bg-gray-100"
            >
              <Camera class="w-4 h-4 text-gray-600" />
            </button>
          </div>
          <div class="text-white">
            <h2 class="text-2xl font-bold">{{ studentInfo?.student_name }}</h2>
            <p class="text-blue-100">{{ studentInfo?.name }}</p>
            <p class="text-blue-100">{{ currentProgram?.program }}</p>
          </div>
        </div>
      </div>

      <!-- Info Sections -->
      <div class="p-6 space-y-8">
        <!-- Personal Information -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <UserCircle class="w-5 h-5 mr-2 text-blue-600" />
            Personal Information
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InfoItem label="Full Name" :value="studentInfo?.student_name" />
            <InfoItem label="Student ID" :value="studentInfo?.name" />
            <InfoItem label="Date of Birth" :value="formatDate(studentInfo?.date_of_birth)" />
            <InfoItem label="Gender" :value="studentInfo?.gender" />
            <InfoItem label="Nationality" :value="studentInfo?.nationality" />
            <InfoItem label="Blood Group" :value="studentInfo?.blood_group || 'Not specified'" />
          </div>
        </div>

        <!-- Academic Information -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <GraduationCap class="w-5 h-5 mr-2 text-blue-600" />
            Academic Information
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InfoItem label="Program" :value="currentProgram?.program" />
            <InfoItem label="Academic Year" :value="currentProgram?.academic_year" />
            <InfoItem label="Academic Term" :value="currentProgram?.academic_term" />
            <InfoItem label="Batch" :value="currentProgram?.student_batch" />
            <InfoItem label="Student Category" :value="currentProgram?.student_category" />
            <InfoItem label="Enrollment Status" value="Active" />
          </div>
        </div>

        <!-- Contact Information -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Phone class="w-5 h-5 mr-2 text-blue-600" />
            Contact Information
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InfoItem label="Email" :value="studentInfo?.student_email_id" />
            <InfoItem label="Mobile" :value="studentInfo?.student_mobile_number || 'Not specified'" />
            <InfoItem label="Address" :value="studentInfo?.address || 'Not specified'" class="md:col-span-2" />
          </div>
        </div>

        <!-- Guardian Information -->
        <div v-if="guardians.length > 0">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Users class="w-5 h-5 mr-2 text-blue-600" />
            Guardian Information
          </h3>
          <div v-for="guardian in guardians" :key="guardian.guardian" class="bg-gray-50 rounded-lg p-4 mb-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoItem label="Guardian Name" :value="guardian.guardian_name" />
              <InfoItem label="Relationship" :value="guardian.relation" />
              <InfoItem label="Email" :value="guardian.email" />
              <InfoItem label="Phone" :value="guardian.mobile" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Dialog -->
    <Dialog
      v-model="showEditDialog"
      :options="{
        size: 'lg',
        title: 'Edit Profile'
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Email"
            v-model="editForm.email"
            type="email"
          />
          <FormControl
            label="Mobile Number"
            v-model="editForm.phone"
            type="text"
          />
          <FormControl
            label="Address"
            v-model="editForm.address"
            type="textarea"
          />
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
          <Button variant="subtle" label="Cancel" @click="showEditDialog = false" />
          <Button
            variant="solid"
            label="Save Changes"
            @click="updateProfile"
            :loading="updateProfileResource.loading"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { createResource, Avatar, Button, Dialog, FormControl } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast } from '@/utils'
import {
  User,
  Camera,
  UserCircle,
  GraduationCap,
  Phone,
  Users
} from 'lucide-vue-next'

// Components
const InfoItem = {
  props: ['label', 'value', 'class'],
  template: `
    <div :class="$props.class">
      <p class="text-sm text-gray-500">{{ label }}</p>
      <p class="font-medium text-gray-900">{{ value || '-' }}</p>
    </div>
  `
}

const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

const showEditDialog = ref(false)
const showPhotoUpload = ref(false)

const editForm = reactive({
  email: '',
  phone: '',
  address: ''
})

// Initialize edit form
const initEditForm = () => {
  editForm.email = studentInfo.value?.student_email_id || ''
  editForm.phone = studentInfo.value?.student_mobile_number || ''
  editForm.address = studentInfo.value?.address || ''
}

// Guardians
const guardians = ref([])
const guardiansResource = createResource({
  url: 'education.education.api.get_student_guardians',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    guardians.value = data || []
  }
})

// Update Profile
const updateProfileResource = createResource({
  url: 'education.education.api.update_student_contact_info',
  onSuccess: () => {
    showEditDialog.value = false
    createToast({
      title: 'Profile updated successfully',
      icon: 'check',
      iconClasses: 'text-green-600'
    })
  },
  onError: (error) => {
    createToast({
      title: error.message || 'Failed to update profile',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const updateProfile = () => {
  updateProfileResource.submit({
    student: studentInfo.value?.name,
    email: editForm.email || null,
    phone: editForm.phone || null,
    address: editForm.address || null
  })
}

// Utility
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  initEditForm()
  if (studentInfo.value?.name) {
    guardiansResource.fetch()
  }
})
</script>
