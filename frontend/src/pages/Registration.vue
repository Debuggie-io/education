<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Course Registration</h1>
      <Badge
        variant="subtle"
        :theme="registrationOpen ? 'green' : 'red'"
        :label="registrationOpen ? 'Registration Open' : 'Registration Closed'"
      />
    </div>

    <!-- Current Enrollment Info -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="font-semibold text-gray-900 mb-4">Current Enrollment</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p class="text-sm text-gray-500">Program</p>
          <p class="font-medium text-gray-900">{{ currentProgram?.program || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Academic Term</p>
          <p class="font-medium text-gray-900">{{ currentProgram?.academic_term || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Academic Year</p>
          <p class="font-medium text-gray-900">{{ currentProgram?.academic_year || 'N/A' }}</p>
        </div>
      </div>
    </div>

    <!-- Registration Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-blue-50 rounded-lg p-4">
        <p class="text-sm text-blue-600">Registered Courses</p>
        <p class="text-2xl font-bold text-blue-900">{{ registeredCourses.length }}</p>
      </div>
      <div class="bg-green-50 rounded-lg p-4">
        <p class="text-sm text-green-600">Available Courses</p>
        <p class="text-2xl font-bold text-green-900">{{ availableCourses.length }}</p>
      </div>
      <div class="bg-purple-50 rounded-lg p-4">
        <p class="text-sm text-purple-600">Total Credits</p>
        <p class="text-2xl font-bold text-purple-900">{{ totalCredits }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="border-b">
        <nav class="flex">
          <button
            @click="activeTab = 'available'"
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'available' 
              ? 'border-blue-600 text-blue-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            Available Courses
          </button>
          <button
            @click="activeTab = 'registered'"
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'registered' 
              ? 'border-blue-600 text-blue-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            My Registered Courses
          </button>
        </nav>
      </div>

      <!-- Loading -->
      <div v-if="coursesLoading" class="flex justify-center py-12">
        <Spinner class="w-8 h-8" />
      </div>

      <!-- Available Courses Tab -->
      <div v-else-if="activeTab === 'available'" class="p-6">
        <div v-if="availableCourses.length === 0" class="text-center py-8">
          <BookOpen class="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900">No Available Courses</h3>
          <p class="text-gray-500">All courses have been registered or none are available.</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="course in availableCourses"
            :key="course.course"
            class="border rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-gray-900">{{ course.course_name }}</h3>
                <p class="text-sm text-gray-500">{{ course.course }}</p>
                <p v-if="course.description" class="text-sm text-gray-600 mt-1">
                  {{ course.description }}
                </p>
              </div>
              <Button
                variant="solid"
                label="Register"
                :disabled="!registrationOpen"
                @click="registerCourse(course)"
                :loading="registeringCourse === course.course"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Registered Courses Tab -->
      <div v-else class="p-6">
        <div v-if="registeredCourses.length === 0" class="text-center py-8">
          <ClipboardList class="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900">No Registered Courses</h3>
          <p class="text-gray-500">You haven't registered for any courses yet.</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="course in registeredCourses"
            :key="course.course"
            class="border rounded-lg p-4"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-gray-900">{{ course.course_name || course.course }}</h3>
                <p class="text-sm text-gray-500">{{ course.course }}</p>
              </div>
              <div class="flex items-center space-x-2">
                <Badge variant="subtle" theme="green" label="Registered" />
                <Button
                  variant="subtle"
                  theme="red"
                  size="sm"
                  label="Drop"
                  :disabled="!registrationOpen"
                  @click="dropCourse(course)"
                  :loading="droppingCourse === course.course"
                />
              </div>
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
import { createToast } from '@/utils'
import { BookOpen, ClipboardList } from 'lucide-vue-next'

const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

const activeTab = ref('available')
const coursesLoading = ref(true)
const availableCourses = ref([])
const registeredCourses = ref([])
const registrationOpen = ref(true) // This would be determined by academic calendar
const registeringCourse = ref(null)
const droppingCourse = ref(null)

const totalCredits = computed(() => registeredCourses.value.length * 3) // Placeholder calculation

// Fetch available courses
const availableCoursesResource = createResource({
  url: 'education.education.api.get_available_courses_for_registration',
  params: {
    student: studentInfo.value?.name,
    program: currentProgram.value?.program
  },
  onSuccess: (data) => {
    availableCourses.value = data || []
    coursesLoading.value = false
  },
  onError: () => {
    coursesLoading.value = false
  }
})

// Register for course
const registerCourseResource = createResource({
  url: 'education.education.api.register_for_course',
  onSuccess: (data) => {
    registeringCourse.value = null
    if (data.success) {
      createToast({
        title: data.message,
        icon: 'check',
        iconClasses: 'text-green-600'
      })
      // Refresh courses
      availableCoursesResource.fetch()
    } else {
      createToast({
        title: data.message,
        icon: 'x',
        iconClasses: 'text-red-600'
      })
    }
  },
  onError: (error) => {
    registeringCourse.value = null
    createToast({
      title: error.message || 'Failed to register',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

// Drop course
const dropCourseResource = createResource({
  url: 'education.education.api.drop_course',
  onSuccess: (data) => {
    droppingCourse.value = null
    if (data.success) {
      createToast({
        title: data.message,
        icon: 'check',
        iconClasses: 'text-green-600'
      })
      // Refresh courses
      availableCoursesResource.fetch()
    } else {
      createToast({
        title: data.message,
        icon: 'x',
        iconClasses: 'text-red-600'
      })
    }
  },
  onError: (error) => {
    droppingCourse.value = null
    createToast({
      title: error.message || 'Failed to drop course',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const registerCourse = (course) => {
  registeringCourse.value = course.course
  registerCourseResource.submit({
    student: studentInfo.value?.name,
    course: course.course,
    academic_term: currentProgram.value?.academic_term
  })
}

const dropCourse = (course) => {
  droppingCourse.value = course.course
  dropCourseResource.submit({
    student: studentInfo.value?.name,
    course: course.course,
    academic_term: currentProgram.value?.academic_term
  })
}

onMounted(() => {
  if (studentInfo.value?.name && currentProgram.value?.program) {
    availableCoursesResource.fetch()
  } else {
    coursesLoading.value = false
  }
})
</script>
