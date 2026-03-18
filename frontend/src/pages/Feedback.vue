<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <h1 class="text-2xl font-semibold text-gray-900">Submit Feedback</h1>

    <!-- Feedback Form -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="max-w-2xl mx-auto">
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Share Your Feedback</h2>
          <p class="text-gray-500 text-sm">
            Your feedback helps us improve. All submissions are reviewed by the appropriate department.
          </p>
        </div>

        <form @submit.prevent="submitFeedback" class="space-y-6">
          <!-- Feedback Type -->
          <FormControl
            label="Feedback Type"
            v-model="form.feedbackType"
            type="select"
            :options="feedbackTypeOptions"
            required
          />

          <!-- Subject -->
          <FormControl
            label="Subject"
            v-model="form.subject"
            type="text"
            placeholder="Brief summary of your feedback"
            required
          />

          <!-- Message -->
          <FormControl
            label="Message"
            v-model="form.message"
            type="textarea"
            placeholder="Please provide details about your feedback..."
            required
          />

          <!-- Anonymous Option -->
          <div class="flex items-center space-x-2">
            <input
              type="checkbox"
              id="anonymous"
              v-model="form.isAnonymous"
              class="rounded border-gray-300"
            />
            <label for="anonymous" class="text-sm text-gray-700">
              Submit anonymously (your identity will not be disclosed)
            </label>
          </div>

          <!-- Info Box -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start space-x-3">
              <Info class="w-5 h-5 text-blue-600 mt-0.5" />
              <div class="text-sm text-blue-800">
                <p class="font-medium">What happens next?</p>
                <ul class="mt-1 list-disc list-inside">
                  <li>Your feedback will be reviewed within 2-3 business days</li>
                  <li>If not anonymous, you may receive a response via email</li>
                  <li>Urgent matters should be reported directly to the relevant office</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end space-x-3">
            <Button
              type="button"
              variant="subtle"
              label="Clear"
              @click="clearForm"
            />
            <Button
              type="submit"
              variant="solid"
              label="Submit Feedback"
              :loading="submitting"
              :disabled="!form.feedbackType || !form.subject || !form.message"
            />
          </div>
        </form>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-3">Common Issues</h3>
        <ul class="space-y-2 text-sm">
          <li>
            <a href="#" class="text-blue-600 hover:underline" @click.prevent="setTemplate('facilities')">
              Facilities & Infrastructure
            </a>
          </li>
          <li>
            <a href="#" class="text-blue-600 hover:underline" @click.prevent="setTemplate('academic')">
              Academic Concerns
            </a>
          </li>
          <li>
            <a href="#" class="text-blue-600 hover:underline" @click.prevent="setTemplate('safety')">
              Safety & Security
            </a>
          </li>
        </ul>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-3">Direct Contacts</h3>
        <ul class="space-y-2 text-sm text-gray-600">
          <li>Dean of Students: dos@ueab.ac.ke</li>
          <li>Academic Affairs: academic@ueab.ac.ke</li>
          <li>Facilities: facilities@ueab.ac.ke</li>
        </ul>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-3">Need Help?</h3>
        <p class="text-sm text-gray-600 mb-3">
          For immediate assistance, visit the Student Services office or call:
        </p>
        <p class="font-medium text-gray-900">+254 xxx xxx xxx</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { createResource, Button, FormControl } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { createToast } from '@/utils'
import { Info } from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const submitting = ref(false)

const form = reactive({
  feedbackType: '',
  subject: '',
  message: '',
  isAnonymous: false
})

const feedbackTypeOptions = [
  { label: 'Select feedback type', value: '' },
  { label: 'Suggestion', value: 'Suggestion' },
  { label: 'Complaint', value: 'Complaint' },
  { label: 'Appreciation', value: 'Appreciation' },
  { label: 'General Feedback', value: 'General' }
]

const submitResource = createResource({
  url: 'education.education.api.submit_feedback',
  onSuccess: (data) => {
    submitting.value = false
    if (data.success) {
      createToast({
        title: data.message,
        icon: 'check',
        iconClasses: 'text-green-600'
      })
      clearForm()
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
      title: error.message || 'Failed to submit feedback',
      icon: 'x',
      iconClasses: 'text-red-600'
    })
  }
})

const submitFeedback = () => {
  submitting.value = true
  submitResource.submit({
    student: studentInfo.value?.name,
    feedback_type: form.feedbackType,
    subject: form.subject,
    message: form.message,
    is_anonymous: form.isAnonymous
  })
}

const clearForm = () => {
  form.feedbackType = ''
  form.subject = ''
  form.message = ''
  form.isAnonymous = false
}

const setTemplate = (type) => {
  const templates = {
    facilities: {
      feedbackType: 'Complaint',
      subject: 'Facilities Issue - ',
      message: 'Location: \n\nDescription of issue: \n\nWhen did this occur: '
    },
    academic: {
      feedbackType: 'General',
      subject: 'Academic Concern - ',
      message: 'Course/Department: \n\nConcern: \n\nSuggested improvement: '
    },
    safety: {
      feedbackType: 'Complaint',
      subject: 'Safety Concern - ',
      message: 'Location: \n\nDescription: \n\nDate/Time: '
    }
  }
  
  if (templates[type]) {
    Object.assign(form, templates[type])
  }
}
</script>
