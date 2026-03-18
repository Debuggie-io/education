<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <h1 class="text-2xl font-semibold text-gray-900">Contact Us</h1>

    <!-- Contact Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- General Inquiries -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-4">
          <Building class="w-6 h-6 text-blue-600" />
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">General Inquiries</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <Phone class="w-4 h-4" />
            <span>+254 xxx xxx xxx</span>
          </div>
          <div class="flex items-center space-x-2">
            <Mail class="w-4 h-4" />
            <span>info@ueab.ac.ke</span>
          </div>
        </div>
      </div>

      <!-- Admissions -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-4">
          <UserPlus class="w-6 h-6 text-green-600" />
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">Admissions</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <Phone class="w-4 h-4" />
            <span>+254 xxx xxx xxx</span>
          </div>
          <div class="flex items-center space-x-2">
            <Mail class="w-4 h-4" />
            <span>admissions@ueab.ac.ke</span>
          </div>
        </div>
      </div>

      <!-- Registrar -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-4">
          <GraduationCap class="w-6 h-6 text-purple-600" />
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">Registrar's Office</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <Phone class="w-4 h-4" />
            <span>+254 xxx xxx xxx</span>
          </div>
          <div class="flex items-center space-x-2">
            <Mail class="w-4 h-4" />
            <span>registrar@ueab.ac.ke</span>
          </div>
        </div>
      </div>

      <!-- Finance -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center mb-4">
          <CreditCard class="w-6 h-6 text-yellow-600" />
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">Finance Department</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <Phone class="w-4 h-4" />
            <span>+254 xxx xxx xxx</span>
          </div>
          <div class="flex items-center space-x-2">
            <Mail class="w-4 h-4" />
            <span>finance@ueab.ac.ke</span>
          </div>
        </div>
      </div>

      <!-- Dean of Students -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
          <Users class="w-6 h-6 text-red-600" />
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">Dean of Students</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <Phone class="w-4 h-4" />
            <span>+254 xxx xxx xxx</span>
          </div>
          <div class="flex items-center space-x-2">
            <Mail class="w-4 h-4" />
            <span>dos@ueab.ac.ke</span>
          </div>
        </div>
      </div>

      <!-- IT Support -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-4">
          <Laptop class="w-6 h-6 text-gray-600" />
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">IT Support</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <Phone class="w-4 h-4" />
            <span>+254 xxx xxx xxx</span>
          </div>
          <div class="flex items-center space-x-2">
            <Mail class="w-4 h-4" />
            <span>itsupport@ueab.ac.ke</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Address & Map -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Physical Address -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="font-semibold text-gray-900 mb-4">Physical Address</h3>
        <div class="flex items-start space-x-3">
          <MapPin class="w-5 h-5 text-gray-400 mt-1" />
          <div class="text-gray-600">
            <p class="font-medium">University of East Africa, Baraton</p>
            <p>P.O. Box 2500-30100</p>
            <p>Eldoret, Kenya</p>
          </div>
        </div>
        
        <div class="mt-6">
          <h4 class="font-medium text-gray-900 mb-2">Office Hours</h4>
          <div class="space-y-1 text-sm text-gray-600">
            <div class="flex items-center justify-between">
              <span>Monday - Thursday</span>
              <span>8:00 AM - 5:00 PM</span>
            </div>
            <div class="flex items-center justify-between">
              <span>Friday</span>
              <span>8:00 AM - 12:00 PM</span>
            </div>
            <div class="flex items-center justify-between">
              <span>Saturday - Sunday</span>
              <span>Closed</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Map Placeholder -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="h-64 bg-gray-200 flex items-center justify-center">
          <div class="text-center text-gray-500">
            <MapPin class="w-12 h-12 mx-auto mb-2" />
            <p>Map View</p>
            <a
              href="https://maps.google.com/?q=University+of+Eastern+Africa+Baraton"
              target="_blank"
              class="text-blue-600 hover:underline text-sm"
            >
              View on Google Maps
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Social Media -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="font-semibold text-gray-900 mb-4">Connect With Us</h3>
      <div class="flex items-center space-x-4">
        <a
          href="#"
          class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white hover:bg-blue-700"
        >
          <span class="text-sm font-bold">f</span>
        </a>
        <a
          href="#"
          class="w-10 h-10 rounded-full bg-sky-500 flex items-center justify-center text-white hover:bg-sky-600"
        >
          <span class="text-sm font-bold">X</span>
        </a>
        <a
          href="#"
          class="w-10 h-10 rounded-full bg-red-600 flex items-center justify-center text-white hover:bg-red-700"
        >
          <span class="text-sm font-bold">YT</span>
        </a>
        <a
          href="#"
          class="w-10 h-10 rounded-full bg-pink-600 flex items-center justify-center text-white hover:bg-pink-700"
        >
          <span class="text-sm font-bold">IG</span>
        </a>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <router-link to="/support/help" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
        <div class="flex items-center space-x-3">
          <HelpCircle class="w-6 h-6 text-blue-600" />
          <span class="font-medium text-gray-900">Help Desk</span>
        </div>
      </router-link>
      <router-link to="/governance/feedback" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
        <div class="flex items-center space-x-3">
          <MessageSquare class="w-6 h-6 text-green-600" />
          <span class="font-medium text-gray-900">Submit Feedback</span>
        </div>
      </router-link>
      <a href="https://ueab.ac.ke" target="_blank" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
        <div class="flex items-center space-x-3">
          <Globe class="w-6 h-6 text-purple-600" />
          <span class="font-medium text-gray-900">University Website</span>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup>
import {
  Building,
  Phone,
  Mail,
  UserPlus,
  GraduationCap,
  CreditCard,
  Users,
  Laptop,
  MapPin,
  HelpCircle,
  MessageSquare,
  Globe
} from 'lucide-vue-next'
</script>
