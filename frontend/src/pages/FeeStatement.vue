<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Fee Statement</h1>
      <div class="flex items-center space-x-2">
        <Button
          variant="subtle"
          icon-left="printer"
          label="Print"
          @click="printStatement"
        />
        <Button
          variant="subtle"
          icon-left="download"
          label="Download PDF"
          @click="downloadPDF"
        />
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-sm text-gray-500">Total Fees</p>
        <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(summaryStats.totalFees) }}</p>
      </div>
      <div class="bg-green-50 rounded-lg shadow p-6">
        <p class="text-sm text-green-600">Amount Paid</p>
        <p class="text-2xl font-bold text-green-700">{{ formatCurrency(summaryStats.amountPaid) }}</p>
      </div>
      <div class="bg-red-50 rounded-lg shadow p-6">
        <p class="text-sm text-red-600">Outstanding Balance</p>
        <p class="text-2xl font-bold text-red-700">{{ formatCurrency(summaryStats.outstandingBalance) }}</p>
      </div>
      <div class="bg-orange-50 rounded-lg shadow p-6">
        <p class="text-sm text-orange-600">Overdue Amount</p>
        <p class="text-2xl font-bold text-orange-700">{{ formatCurrency(summaryStats.overdueAmount) }}</p>
      </div>
    </div>

    <!-- Pay Now Button -->
    <div v-if="summaryStats.outstandingBalance > 0" class="bg-blue-50 rounded-lg p-4 flex items-center justify-between">
      <div>
        <p class="font-semibold text-blue-900">You have an outstanding balance</p>
        <p class="text-sm text-blue-700">Pay now to avoid late fees and academic holds.</p>
      </div>
      <router-link to="/finance/pay">
        <Button variant="solid" label="Pay Now" icon-left="credit-card" />
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="invoicesLoading" class="flex justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Invoices -->
    <div v-else-if="invoices.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <Receipt class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Fee Records</h3>
      <p class="text-gray-500">No fee statements have been generated for your account.</p>
    </div>

    <!-- Invoices Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b">
        <h2 class="text-lg font-semibold text-gray-900">Invoice History</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invoice
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Program
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="invoice in invoices" :key="invoice.invoice">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ invoice.invoice }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ invoice.program || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge
                  variant="subtle"
                  :theme="getStatusColor(invoice.status)"
                  :label="invoice.status"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ invoice.due_date !== '-' ? formatDate(invoice.due_date) : '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ invoice.amount }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <div class="flex items-center justify-end space-x-2">
                  <Button
                    v-if="invoice.status === 'Paid'"
                    variant="subtle"
                    size="sm"
                    icon-left="download"
                    label="Receipt"
                    @click="downloadInvoice(invoice)"
                  />
                  <router-link
                    v-if="invoice.status !== 'Paid'"
                    :to="{ path: '/finance/pay', query: { invoice: invoice.invoice } }"
                  >
                    <Button
                      variant="solid"
                      size="sm"
                      label="Pay"
                    />
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Payment History Link -->
    <div class="text-center">
      <router-link to="/finance/history" class="text-blue-600 hover:underline">
        View Full Payment History →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'
import { parseCurrencyValue, formatCurrency, formatDate } from '@/utils'
import { Receipt } from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = computed(() => getStudentInfo().value)

const invoices = ref([])
const invoicesLoading = ref(true)
const printFormat = ref('Standard')

const summaryStats = computed(() => {
  let totalFees = 0
  let amountPaid = 0
  let outstandingBalance = 0
  let overdueAmount = 0

  invoices.value.forEach((inv) => {
    const amount = parseCurrencyValue(inv.amount)
    
    if (inv.status === 'Paid') {
      amountPaid += amount
      totalFees += amount
    } else {
      outstandingBalance += amount
      totalFees += amount
      if (inv.status === 'Overdue') {
        overdueAmount += amount
      }
    }
  })

  return { totalFees, amountPaid, outstandingBalance, overdueAmount }
})

// Fetch invoices
const invoicesResource = createResource({
  url: 'education.education.api.get_student_invoices',
  params: {
    student: studentInfo.value?.name
  },
  onSuccess: (data) => {
    invoices.value = data?.invoices || []
    printFormat.value = data?.print_format || 'Standard'
    invoicesLoading.value = false
  },
  onError: () => {
    invoicesLoading.value = false
  }
})

const getStatusColor = (status) => {
  const colors = {
    'Paid': 'green',
    'Unpaid': 'red',
    'Overdue': 'red',
    'Partly Paid': 'orange'
  }
  return colors[status] || 'gray'
}

const downloadInvoice = (invoice) => {
  const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent('Sales Invoice')}&name=${encodeURIComponent(invoice.invoice)}&format=${encodeURIComponent(printFormat.value)}`
  window.open(url, '_blank')
}

const printStatement = () => {
  window.print()
}

const downloadPDF = () => {
  // TODO: Generate and download full statement PDF
  printStatement()
}

onMounted(() => {
  if (studentInfo.value?.name) {
    invoicesResource.fetch()
  } else {
    invoicesLoading.value = false
  }
})
</script>
