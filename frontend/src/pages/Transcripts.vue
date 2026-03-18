<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Academic Transcript</h1>
      <div class="flex items-center space-x-2">
        <Button
          variant="subtle"
          icon-left="printer"
          label="Print"
          @click="printTranscript"
        />
        <Button
          variant="solid"
          icon-left="download"
          label="Request Official Copy"
          @click="showRequestDialog = true"
        />
      </div>
    </div>

    <!-- Student Info -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <p class="text-sm text-gray-500">Student Name</p>
          <p class="font-semibold text-gray-900">{{ transcriptData?.student_name }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Student ID</p>
          <p class="font-semibold text-gray-900">{{ transcriptData?.student }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Email</p>
          <p class="font-semibold text-gray-900">{{ transcriptData?.student_email }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Generated On</p>
          <p class="font-semibold text-gray-900">{{ currentDate }}</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="transcriptLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Data -->
    <div v-else-if="!transcriptData?.programs?.length" class="bg-white rounded-lg shadow p-12 text-center">
      <FileText class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Transcript Data</h3>
      <p class="text-gray-500">Your academic records are not yet available.</p>
    </div>

    <!-- Programs -->
    <div v-else class="space-y-6">
      <div
        v-for="program in transcriptData.programs"
        :key="program.program"
        class="bg-white rounded-lg shadow overflow-hidden"
      >
        <!-- Program Header -->
        <div class="bg-blue-600 text-white px-6 py-4">
          <h2 class="text-lg font-semibold">{{ program.program }}</h2>
          <p class="text-blue-100">{{ program.academic_year }} • Batch: {{ program.batch || 'N/A' }}</p>
        </div>

        <!-- Terms -->
        <div class="divide-y">
          <div
            v-for="term in program.terms"
            :key="term.term"
            class="p-6"
          >
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-semibold text-gray-900">{{ term.term }}</h3>
              <Badge
                variant="subtle"
                theme="blue"
                :label="'GPA: ' + (term.gpa || 0).toFixed(2)"
              />
            </div>

            <table class="min-w-full">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-2 text-sm font-medium text-gray-500">Course</th>
                  <th class="text-left py-2 text-sm font-medium text-gray-500">Assessment</th>
                  <th class="text-center py-2 text-sm font-medium text-gray-500">Score</th>
                  <th class="text-center py-2 text-sm font-medium text-gray-500">Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="course in term.courses"
                  :key="course.course + course.assessment_group"
                  class="border-b last:border-0"
                >
                  <td class="py-3 text-gray-900">{{ course.course }}</td>
                  <td class="py-3 text-gray-600">{{ course.assessment_group }}</td>
                  <td class="py-3 text-center text-gray-900">
                    {{ course.total_score }}/{{ course.maximum_score }}
                  </td>
                  <td class="py-3 text-center">
                    <Badge
                      variant="subtle"
                      :theme="getGradeColor(course.grade)"
                      :label="course.grade || '-'"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Official Transcript Dialog -->
    <Dialog
      v-model="showRequestDialog"
      :options="{
        size: 'md',
        title: 'Request Official Transcript'
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Number of Copies"
            v-model="requestForm.copies"
            type="number"
            :min="1"
            :max="10"
          />
          <FormControl
            label="Delivery Method"
            v-model="requestForm.deliveryMethod"
            type="select"
            :options="[
              { label: 'Pickup from Office', value: 'Pickup' },
              { label: 'Mail to Address', value: 'Mail' }
            ]"
          />
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p class="text-sm text-yellow-800">
              <strong>Note:</strong> Official transcript requests may take 3-5 business days to process.
              Additional fees may apply.
            </p>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
          <Button variant="subtle" label="Cancel" @click="showRequestDialog = false" />
          <Button
            variant="solid"
            label="Submit Request"
            @click="submitTranscriptRequest"
            :loading="requestLoading"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Spinner, Dialog, FormControl } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast } from '@/utils'
import { FileText } from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const transcriptData = ref(null)
const transcriptLoading = ref(true)
const showRequestDialog = ref(false)
const requestLoading = ref(false)

const requestForm = reactive({
  copies: 1,
  deliveryMethod: 'Pickup'
})

const currentDate = new Date().toLocaleDateString('en-US', {
  year: 'numeric',
  month: 'long',
  day: 'numeric'
})

// Fetch transcript data
const transcriptResource = createResource({
  url: 'education.education.api.get_transcript_data',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    transcriptData.value = data
    transcriptLoading.value = false
  },
  onError: () => {
    transcriptLoading.value = false
  }
})

// Request transcript
const requestTranscriptResource = createResource({
  url: 'education.education.api.request_official_transcript',
  onSuccess: (data) => {
    requestLoading.value = false
    showRequestDialog.value = false
    createToast({
      title: data.message || 'Transcript request submitted',
      icon: 'check',
      iconClasses: 'text-green-600'
    })
  },
  onError: (error) => {
    requestLoading.value = false
    createToast({
      title: error.message || 'Failed to submit request',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const submitTranscriptRequest = () => {
  requestLoading.value = true
  requestTranscriptResource.submit({
    student: studentInfo.value?.name,
    copies: requestForm.copies,
    delivery_method: requestForm.deliveryMethod
  })
}

const printTranscript = () => {
  window.print()
}

const getGradeColor = (grade) => {
  if (!grade) return 'gray'
  const g = grade.toUpperCase()
  if (g === 'A' || g === 'A+') return 'green'
  if (g === 'B' || g === 'B+') return 'blue'
  if (g === 'C' || g === 'C+') return 'yellow'
  if (g === 'D') return 'orange'
  return 'red'
}

onMounted(() => {
  if (studentInfo.value?.name) {
    transcriptResource.fetch()
  } else {
    transcriptLoading.value = false
  }
})
</script>
