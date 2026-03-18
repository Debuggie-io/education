import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { studentStore } from '@/stores/student'

const routes = [
  // Main
  { path: '/', redirect: '/dashboard' },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/pages/Notifications.vue'),
  },

  // Academics
  {
    path: '/academics/courses',
    name: 'Courses',
    component: () => import('@/pages/Courses.vue'),
  },
  {
    path: '/academics/schedule',
    name: 'Schedule',
    component: () => import('@/pages/Schedule.vue'),
  },
  {
    path: '/schedule',
    redirect: '/academics/schedule',
  },
  {
    path: '/academics/attendance',
    name: 'Attendance',
    component: () => import('@/pages/Attendance.vue'),
  },
  {
    path: '/attendance',
    redirect: '/academics/attendance',
  },
  {
    path: '/academics/grades',
    name: 'Grades',
    component: () => import('@/pages/Grades.vue'),
  },
  {
    path: '/grades',
    redirect: '/academics/grades',
  },
  {
    path: '/academics/transcripts',
    name: 'Transcripts',
    component: () => import('@/pages/Transcripts.vue'),
  },
  {
    path: '/academics/registration',
    name: 'Registration',
    component: () => import('@/pages/Registration.vue'),
  },

  // Finance
  {
    path: '/finance/statement',
    name: 'FeeStatement',
    component: () => import('@/pages/FeeStatement.vue'),
  },
  {
    path: '/finance/pay',
    name: 'PayFees',
    component: () => import('@/pages/Fees.vue'),
  },
  {
    path: '/fees',
    redirect: '/finance/statement',
  },
  {
    path: '/finance/history',
    name: 'PaymentHistory',
    component: () => import('@/pages/PaymentHistory.vue'),
  },

  // Residence
  {
    path: '/residence/room',
    name: 'MyRoom',
    component: () => import('@/pages/MyRoom.vue'),
  },
  {
    path: '/residence/apply',
    name: 'ApplyHousing',
    component: () => import('@/pages/ApplyHousing.vue'),
  },
  {
    path: '/residence/maintenance',
    name: 'MaintenanceRequest',
    component: () => import('@/pages/MaintenanceRequest.vue'),
  },

  // Graduation
  {
    path: '/graduation/status',
    name: 'GraduationStatus',
    component: () => import('@/pages/GraduationStatus.vue'),
  },
  {
    path: '/graduation/audit',
    name: 'DegreeAudit',
    component: () => import('@/pages/DegreeAudit.vue'),
  },
  {
    path: '/graduation/clearance',
    name: 'Clearance',
    component: () => import('@/pages/Clearance.vue'),
  },

  // Governance
  {
    path: '/governance/council',
    name: 'StudentCouncil',
    component: () => import('@/pages/StudentCouncil.vue'),
  },
  {
    path: '/governance/clubs',
    name: 'Clubs',
    component: () => import('@/pages/Clubs.vue'),
  },
  {
    path: '/governance/events',
    name: 'Events',
    component: () => import('@/pages/Events.vue'),
  },
  {
    path: '/governance/feedback',
    name: 'Feedback',
    component: () => import('@/pages/Feedback.vue'),
  },

  // Support
  {
    path: '/support/leave',
    name: 'LeaveApplication',
    component: () => import('@/pages/LeaveApplication.vue'),
  },
  {
    path: '/support/help',
    name: 'HelpDesk',
    component: () => import('@/pages/HelpDesk.vue'),
  },
  {
    path: '/support/contact',
    name: 'ContactUs',
    component: () => import('@/pages/ContactUs.vue'),
  },

  // Catch-all
  {
    path: '/:catchAll(.*)',
    redirect: '/dashboard',
  },
]

let router = createRouter({
  history: createWebHistory('/student-portal'),
  routes,
})

router.beforeEach(async (to, from) => {
  const { isLoggedIn, user: sessionUser } = sessionStore()
  const { user } = usersStore()
  const { student } = studentStore()

  if (!isLoggedIn) {
    window.location.href = '/login'
    return await next(false)
  }

  if (user.data.length === 0) {
    await user.reload()
  }
  await student.reload()
})

export default router
