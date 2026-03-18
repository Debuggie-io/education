<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">My Courses</h1>
      <router-link to="/academics/registration">
        <Button
          variant="solid"
          icon-left="plus"
          label="Register for Course"
        />
      </router-link>
    </div>

    <!-- Program Info -->
    <div class="bg-blue-50 rounded-lg p-4 flex items-center justify-between">
      <div>
        <p class="text-sm text-blue-600">Current Program</p>
        <p class="font-semibold text-blue-900">{{ currentProgram?.program }}</p>
      </div>
      <div>
        <p class="text-sm text-blue-600">Academic Term</p>
        <p class="font-semibold text-blue-900">{{ currentProgram?.academic_term || 'N/A' }}</p>
      </div>
      <div>
        <p class="text-sm text-blue-600">Batch</p>
        <p class="font-semibold text-blue-900">{{ currentProgram?.student_batch || 'N/A' }}</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="coursesLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Courses -->
    <div v-else-if="courses.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <BookOpen class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Courses Found</h3>
      <p class="text-gray-500 mb-4">You haven't enrolled in any courses yet.</p>
      <router-link to="/academics/registration">
        <Button variant="solid" label="Browse Available Courses" />
      </router-link>
    </div>

    <!-- Courses Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="course in courses"
        :key="course.course"
        class="bg-white rounded-lg shadow overflow-hidden hover:shadow-md transition-shadow"
      >
        <div class="h-2" :class="getColorClass(course.course)"></div>
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900">{{ course.course_name || course.course }}</h3>
              <p class="text-sm text-gray-500">{{ course.course }}</p>
            </div>
            <Badge
              variant="subtle"
              :theme="course.status === 'Completed' ? 'green' : 'blue'"
              :label="course.status || 'Active'"
            />
          </div>
          
          <div class="space-y-2 text-sm">
            <div v-if="course.instructor" class="flex items-center text-gray-600">
              <User class="w-4 h-4 mr-2" />
              {{ course.instructor }}
            </div>
            <div v-if="course.schedule" class="flex items-center text-gray-600">
              <Clock class="w-4 h-4 mr-2" />
              {{ course.schedule }}
            </div>
            <div v-if="course.room" class="flex items-center text-gray-600">
              <MapPin class="w-4 h-4 mr-2" />
              {{ course.room }}
            </div>
          </div>

          <div class="mt-4 pt-4 border-t flex items-center justify-end">
            <Button
              variant="subtle"
              size="sm"
              label="View Details"
              @click="viewCourseDetails(course)"
            />
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
import { BookOpen, User, Clock, MapPin } from 'lucide-vue-next'

const { getStudentInfo, getCurrentProgram } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)
const currentProgram = computed(() => getCurrentProgram().value)

const courses = ref([])
const coursesLoading = ref(true)

// Fetch course list
const coursesResource = createResource({
  url: 'education.education.api.get_course_list_based_on_program',
  params: {
    program_name: currentProgram.value?.program
  },
  onSuccess: async (courseIds) => {
    // Get course details for each course
    const courseDetails = []
    for (const courseId of courseIds) {
      courseDetails.push({
        course: courseId,
        course_name: courseId,
        status: 'Active'
      })
    }
    courses.value = courseDetails
    coursesLoading.value = false
  },
  onError: () => {
    coursesLoading.value = false
  }
})

onMounted(() => {
  if (currentProgram.value?.program) {
    coursesResource.fetch()
  } else {
    coursesLoading.value = false
  }
})

const viewCourseDetails = (course) => {
  // TODO: Navigate to course details
  console.log('View course:', course)
}

const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-pink-500', 'bg-teal-500']

const getColorClass = (courseId) => {
  const index = courseId.charCodeAt(0) % colors.length
  return colors[index]
}
</script>
