<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Help Desk</h1>
      <Button
        variant="solid"
        icon-left="plus"
        label="New Ticket"
        @click="showNewTicketDialog = true"
      />
    </div>

    <!-- Search & Filter -->
    <div class="flex items-center space-x-4">
      <FormControl
        type="text"
        v-model="searchQuery"
        placeholder="Search tickets..."
        class="flex-1 max-w-md"
      />
      <FormControl
        type="select"
        v-model="statusFilter"
        :options="statusOptions"
        class="w-40"
      />
    </div>

    <!-- Quick Help -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div
        v-for="item in quickHelp"
        :key="item.title"
        class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
        @click="handleQuickHelp(item)"
      >
        <div class="flex items-center space-x-3">
          <div :class="`w-10 h-10 rounded-full ${item.bgColor} flex items-center justify-center`">
            <component :is="item.icon" :class="`w-5 h-5 ${item.iconColor}`" />
          </div>
          <div>
            <p class="font-medium text-gray-900">{{ item.title }}</p>
            <p class="text-sm text-gray-500">{{ item.subtitle }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tickets List -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b">
        <h2 class="text-lg font-semibold text-gray-900">My Tickets</h2>
      </div>

      <!-- Empty State -->
      <div class="p-12 text-center">
        <Ticket class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Support Tickets</h3>
        <p class="text-gray-500 mb-4">You haven't submitted any support tickets yet.</p>
        <Button
          variant="solid"
          label="Create Your First Ticket"
          @click="showNewTicketDialog = true"
        />
      </div>
    </div>

    <!-- FAQ Section -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Frequently Asked Questions</h2>
      <div class="space-y-4">
        <div
          v-for="faq in faqs"
          :key="faq.question"
          class="border-b pb-4 last:border-0"
        >
          <button
            class="flex items-center justify-between w-full text-left"
            @click="faq.open = !faq.open"
          >
            <span class="font-medium text-gray-900">{{ faq.question }}</span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': faq.open }"
            />
          </button>
          <p v-if="faq.open" class="mt-2 text-gray-600 text-sm">
            {{ faq.answer }}
          </p>
        </div>
      </div>
    </div>

    <!-- New Ticket Dialog -->
    <Dialog
      v-model="showNewTicketDialog"
      :options="{ size: 'lg', title: 'Create Support Ticket' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Category"
            v-model="newTicket.category"
            type="select"
            :options="categoryOptions"
            required
          />
          <FormControl
            label="Subject"
            v-model="newTicket.subject"
            type="text"
            placeholder="Brief description of your issue"
            required
          />
          <FormControl
            label="Description"
            v-model="newTicket.description"
            type="textarea"
            placeholder="Please provide detailed information about your issue..."
            required
          />
          <FormControl
            label="Priority"
            v-model="newTicket.priority"
            type="select"
            :options="priorityOptions"
          />
        </div>
      </template>
      <template #actions>
        <div class="flex space-x-2">
          <Button variant="subtle" label="Cancel" @click="showNewTicketDialog = false" />
          <Button
            variant="solid"
            label="Submit Ticket"
            @click="submitTicket"
            :loading="submittingTicket"
            :disabled="!newTicket.category || !newTicket.subject || !newTicket.description"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Button, FormControl, Dialog } from 'frappe-ui'
import { createToast } from '@/utils'
import {
  Ticket,
  ChevronDown,
  Key,
  CreditCard,
  GraduationCap,
  Laptop
} from 'lucide-vue-next'

const searchQuery = ref('')
const statusFilter = ref('all')
const showNewTicketDialog = ref(false)
const submittingTicket = ref(false)

const newTicket = reactive({
  category: '',
  subject: '',
  description: '',
  priority: 'Medium'
})

const statusOptions = [
  { label: 'All Status', value: 'all' },
  { label: 'Open', value: 'open' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Resolved', value: 'resolved' },
  { label: 'Closed', value: 'closed' }
]

const categoryOptions = [
  { label: 'Select category', value: '' },
  { label: 'Academic Issues', value: 'Academic' },
  { label: 'Technical Support', value: 'Technical' },
  { label: 'Financial', value: 'Financial' },
  { label: 'Account/Login', value: 'Account' },
  { label: 'Other', value: 'Other' }
]

const priorityOptions = [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' }
]

const quickHelp = [
  {
    title: 'Password Reset',
    subtitle: 'Reset your login',
    icon: Key,
    bgColor: 'bg-blue-100',
    iconColor: 'text-blue-600',
    action: 'password'
  },
  {
    title: 'Fee Payment',
    subtitle: 'Payment issues',
    icon: CreditCard,
    bgColor: 'bg-green-100',
    iconColor: 'text-green-600',
    action: 'payment'
  },
  {
    title: 'Course Issues',
    subtitle: 'Registration help',
    icon: GraduationCap,
    bgColor: 'bg-purple-100',
    iconColor: 'text-purple-600',
    action: 'course'
  },
  {
    title: 'Technical Help',
    subtitle: 'Portal issues',
    icon: Laptop,
    bgColor: 'bg-orange-100',
    iconColor: 'text-orange-600',
    action: 'technical'
  }
]

const faqs = reactive([
  {
    question: 'How do I reset my password?',
    answer: 'Click on "Forgot Password" on the login page, enter your email, and follow the instructions sent to your inbox.',
    open: false
  },
  {
    question: 'How can I view my fee statement?',
    answer: 'Navigate to Finance > Fee Statement to view all your invoices and payment history.',
    open: false
  },
  {
    question: 'How do I register for courses?',
    answer: 'Go to Academics > Registration during the registration period to select and register for your courses.',
    open: false
  },
  {
    question: 'How can I apply for a leave?',
    answer: 'Visit Academics > Attendance and click on "Apply Leave" to submit a leave application.',
    open: false
  }
])

const handleQuickHelp = (item) => {
  newTicket.category = item.action === 'password' ? 'Account'
    : item.action === 'payment' ? 'Financial'
    : item.action === 'course' ? 'Academic'
    : 'Technical'
  showNewTicketDialog.value = true
}

const submitTicket = () => {
  submittingTicket.value = true
  // Simulate API call
  setTimeout(() => {
    submittingTicket.value = false
    showNewTicketDialog.value = false
    createToast({
      title: 'Support ticket created successfully',
      icon: 'check',
      iconClasses: 'text-green-600'
    })
    // Reset form
    newTicket.category = ''
    newTicket.subject = ''
    newTicket.description = ''
    newTicket.priority = 'Medium'
  }, 1000)
}
</script>
