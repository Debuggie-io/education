<template>
  <div
    class="flex h-full flex-col justify-between transition-all duration-300 ease-in-out"
    :class="isSidebarCollapsed ? 'w-12' : 'w-56'"
  >
    <div class="flex flex-col overflow-hidden">
      <UserDropdown
        class="p-2"
        :isCollapsed="isSidebarCollapsed"
        :educationSettings="
          !educationSettings.loading && educationSettings.data
        "
      />
      <div class="flex flex-col overflow-y-auto">
        <!-- Main Navigation -->
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in mainLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
        
        <!-- Academics Section -->
        <div v-if="!isSidebarCollapsed" class="px-4 pt-4 pb-1">
          <span class="text-xs font-semibold text-gray-400 uppercase">Academics</span>
        </div>
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in academicsLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
        
        <!-- Finance Section -->
        <div v-if="!isSidebarCollapsed" class="px-4 pt-4 pb-1">
          <span class="text-xs font-semibold text-gray-400 uppercase">Finance</span>
        </div>
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in financeLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
        
        <!-- Residence Section -->
        <div v-if="!isSidebarCollapsed" class="px-4 pt-4 pb-1">
          <span class="text-xs font-semibold text-gray-400 uppercase">Residence</span>
        </div>
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in residenceLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
        
        <!-- Graduation Section -->
        <div v-if="!isSidebarCollapsed" class="px-4 pt-4 pb-1">
          <span class="text-xs font-semibold text-gray-400 uppercase">Graduation</span>
        </div>
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in graduationLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
        
        <!-- Campus Life Section -->
        <div v-if="!isSidebarCollapsed" class="px-4 pt-4 pb-1">
          <span class="text-xs font-semibold text-gray-400 uppercase">Campus Life</span>
        </div>
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in campusLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
        
        <!-- Support Section -->
        <div v-if="!isSidebarCollapsed" class="px-4 pt-4 pb-1">
          <span class="text-xs font-semibold text-gray-400 uppercase">Support</span>
        </div>
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in supportLinks"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
      </div>
    </div>
    <SidebarLink
      :label="isSidebarCollapsed ? 'Expand' : 'Collapse'"
      :isCollapsed="isSidebarCollapsed"
      @click="isSidebarCollapsed = !isSidebarCollapsed"
      class="m-2"
    >
      <template #icon>
        <span class="grid h-5 w-6 flex-shrink-0 place-items-center">
          <ArrowLeftToLine
            class="h-4.5 w-4.5 text-gray-700 duration-300 ease-in-out"
            :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }"
          />
        </span>
      </template>
    </SidebarLink>
  </div>
</template>

<script setup>
import { useStorage } from '@vueuse/core'
import SidebarLink from '@/components/SidebarLink.vue'
import {
  LayoutDashboard,
  CalendarCheck,
  GraduationCap,
  Banknote,
  UserCheck,
  ArrowLeftToLine,
  BookOpen,
  User,
  Bell,
  FileText,
  CreditCard,
  Receipt,
  Home,
  Wrench,
  Award,
  ClipboardList,
  CheckSquare,
  Users,
  Calendar,
  MessageSquare,
  HelpCircle,
  Phone,
} from 'lucide-vue-next'

import UserDropdown from './UserDropdown.vue'
import { createResource } from 'frappe-ui'

// Main navigation links
const mainLinks = [
  {
    label: 'Dashboard',
    to: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Profile',
    to: '/profile',
    icon: User,
  },
  {
    label: 'Notifications',
    to: '/notifications',
    icon: Bell,
  },
]

// Academics links
const academicsLinks = [
  {
    label: 'My Courses',
    to: '/academics/courses',
    icon: BookOpen,
  },
  {
    label: 'Schedule',
    to: '/academics/schedule',
    icon: CalendarCheck,
  },
  {
    label: 'Grades',
    to: '/academics/grades',
    icon: GraduationCap,
  },
  {
    label: 'Attendance',
    to: '/academics/attendance',
    icon: UserCheck,
  },
  {
    label: 'Transcripts',
    to: '/academics/transcripts',
    icon: FileText,
  },
  {
    label: 'Registration',
    to: '/academics/registration',
    icon: ClipboardList,
  },
]

// Finance links
const financeLinks = [
  {
    label: 'Fee Statement',
    to: '/finance/statement',
    icon: Receipt,
  },
  {
    label: 'Pay Fees',
    to: '/finance/pay',
    icon: CreditCard,
  },
  {
    label: 'Payment History',
    to: '/finance/history',
    icon: Banknote,
  },
]

// Residence links
const residenceLinks = [
  {
    label: 'My Room',
    to: '/residence/room',
    icon: Home,
  },
  {
    label: 'Maintenance',
    to: '/residence/maintenance',
    icon: Wrench,
  },
]

// Graduation links
const graduationLinks = [
  {
    label: 'Status',
    to: '/graduation/status',
    icon: Award,
  },
  {
    label: 'Degree Audit',
    to: '/graduation/audit',
    icon: ClipboardList,
  },
  {
    label: 'Clearance',
    to: '/graduation/clearance',
    icon: CheckSquare,
  },
]

// Campus life links
const campusLinks = [
  {
    label: 'Student Council',
    to: '/governance/council',
    icon: Users,
  },
  {
    label: 'Clubs',
    to: '/governance/clubs',
    icon: Users,
  },
  {
    label: 'Events',
    to: '/governance/events',
    icon: Calendar,
  },
  {
    label: 'Feedback',
    to: '/governance/feedback',
    icon: MessageSquare,
  },
]

// Support links
const supportLinks = [
  {
    label: 'Apply Leave',
    to: '/support/leave',
    icon: Calendar,
  },
  {
    label: 'Help Desk',
    to: '/support/help',
    icon: HelpCircle,
  },
  {
    label: 'Contact Us',
    to: '/support/contact',
    icon: Phone,
  },
]

const isSidebarCollapsed = useStorage('sidebar_is_collapsed', false)

// create a resource which call the function get_school_abbr_logo in api file using createResource
const educationSettings = createResource({
  url: 'education.education.api.get_school_abbr_logo',
  auto: true,
})
</script>
