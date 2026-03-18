<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Payment History</h1>
      <router-link to="/finance/statement">
        <Button variant="subtle" icon-left="file-text" label="View Statement" />
      </router-link>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-green-50 rounded-lg p-6">
        <p class="text-sm text-green-600">Total Payments Made</p>
        <p class="text-2xl font-bold text-green-700">{{ formatCurrency(totalPaid) }}</p>
      </div>
      <div class="bg-blue-50 rounded-lg p-6">
        <p class="text-sm text-blue-600">Number of Payments</p>
        <p class="text-2xl font-bold text-blue-700">{{ payments.length }}</p>
      </div>
      <div class="bg-purple-50 rounded-lg p-6">
        <p class="text-sm text-purple-600">Last Payment</p>
        <p class="text-2xl font-bold text-purple-700">{{ lastPaymentDate }}</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="paymentsLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Payments -->
    <div v-else-if="payments.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <CreditCard class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Payment History</h3>
      <p class="text-gray-500 mb-4">You haven't made any payments yet.</p>
      <router-link to="/finance/pay">
        <Button variant="solid" label="Make a Payment" />
      </router-link>
    </div>

    <!-- Payments Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">All Payments</h2>
        <div class="flex items-center space-x-2">
          <FormControl
            type="select"
            v-model="filterYear"
            :options="yearOptions"
            placeholder="Filter by year"
          />
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reference
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invoice
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Program
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Receipt
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="payment in filteredPayments" :key="payment.name">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDate(payment.payment_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ payment.name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ payment.invoice }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ payment.program || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex items-center">
                  <component :is="getPaymentMethodIcon(payment.payment_method)" class="w-4 h-4 mr-2 text-gray-400" />
                  {{ payment.payment_method || 'Bank Transfer' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600 text-right">
                {{ payment.amount }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <Button
                  variant="subtle"
                  size="sm"
                  icon-left="download"
                  @click="downloadReceipt(payment)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Spinner, FormControl } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { CreditCard, Smartphone, Building, DollarSign } from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const payments = ref([])
const paymentsLoading = ref(true)
const filterYear = ref('')

const yearOptions = computed(() => {
  const years = new Set()
  payments.value.forEach(p => {
    if (p.payment_date) {
      years.add(new Date(p.payment_date).getFullYear().toString())
    }
  })
  return [
    { label: 'All Years', value: '' },
    ...Array.from(years).sort().reverse().map(y => ({ label: y, value: y }))
  ]
})

const filteredPayments = computed(() => {
  if (!filterYear.value) return payments.value
  return payments.value.filter(p => {
    return p.payment_date && new Date(p.payment_date).getFullYear().toString() === filterYear.value
  })
})

const totalPaid = computed(() => {
  return payments.value.reduce((sum, p) => {
    const amount = parseFloat(p.amount?.replace(/[^0-9.-]+/g, '') || 0)
    return sum + amount
  }, 0)
})

const lastPaymentDate = computed(() => {
  if (payments.value.length === 0) return 'N/A'
  const dates = payments.value
    .filter(p => p.payment_date && p.payment_date !== '-')
    .map(p => new Date(p.payment_date))
  if (dates.length === 0) return 'N/A'
  const latest = new Date(Math.max(...dates))
  return formatDate(latest)
})

// Fetch paid invoices as payment history
const paymentsResource = createResource({
  url: 'education.education.api.get_student_invoices',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    // Filter only paid invoices
    const paidInvoices = (data?.invoices || []).filter(inv => inv.status === 'Paid')
    payments.value = paidInvoices.map(inv => ({
      name: inv.invoice,
      invoice: inv.invoice,
      program: inv.program,
      amount: inv.amount,
      payment_date: inv.payment_date,
      payment_method: 'Bank Transfer' // Placeholder
    }))
    paymentsLoading.value = false
  },
  onError: () => {
    paymentsLoading.value = false
  }
})

const formatCurrency = (amount) => {
  return 'KES ' + amount.toLocaleString('en-US', { minimumFractionDigits: 2 })
}

const formatDate = (date) => {
  if (!date || date === '-') return '-'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getPaymentMethodIcon = (method) => {
  const icons = {
    'M-Pesa': Smartphone,
    'Bank Transfer': Building,
    'Cash': DollarSign,
    'Credit Card': CreditCard
  }
  return icons[method] || CreditCard
}

const downloadReceipt = (payment) => {
  const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent('Sales Invoice')}&name=${encodeURIComponent(payment.invoice)}&format=${encodeURIComponent('Standard')}`
  window.open(url, '_blank')
}

onMounted(() => {
  if (studentInfo.value?.name) {
    paymentsResource.fetch()
  } else {
    paymentsLoading.value = false
  }
})
</script>
