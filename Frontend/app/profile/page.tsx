'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Cookies from 'js-cookie'
import { 
  ArrowLeft, 
  User, 
  Settings, 
  Bell, 
  Globe, 
  Shield, 
  HelpCircle, 
  LogOut,
  Wallet,
  Building2,
  Mail,
  Phone,
  Edit
} from 'lucide-react'
import Link from 'next/link'

const API_BASE_URL = 'http://192.168.5.38:5000'

interface UserData {
  totalBalance: number
  accountsCount: number
  accounts: Array<{
    id: string
    account_name: string
    bank_name: string
    balance: number
    currency: string
  }>
  monthlyIncome: number
  monthlySpending: number
  savingsRate: number
}

export default function ProfilePage() {
  const [userData, setUserData] = useState<UserData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [notifications, setNotifications] = useState(true)
  const [language, setLanguage] = useState('en')
  const router = useRouter()

  useEffect(() => {
    const userId = Cookies.get('userId')
    if (!userId) {
      router.push('/auth/register')
      return
    }
    
    loadUserData(userId)
  }, [router])

  const loadUserData = async (userId: string) => {
    try {
      setIsLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/insights/dashboard/${userId}`)
      setUserData(response.data)
    } catch (error) {
      console.error('Failed to load user data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    // Clear all cookies
    Cookies.remove('userId')
    Cookies.remove('customerUserId')
    Cookies.remove('userEmail')
    
    // Redirect to register page
    router.push('/auth/register')
  }

  const formatCurrency = (amount: number, currency = 'SAR') => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    )
  }

  const userEmail = Cookies.get('userEmail') || 'user@example.com'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <ArrowLeft className="h-6 w-6 text-gray-600" />
            </Link>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Profile</h1>
              <p className="text-sm text-gray-500">Manage your account and preferences</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Profile Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center">
              <User className="h-10 w-10 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">User Name</h2>
              <p className="text-gray-600 flex items-center mt-1">
                <Mail className="h-4 w-4 mr-2" />
                {userEmail}
              </p>
              <p className="text-gray-600 flex items-center mt-1">
                <Phone className="h-4 w-4 mr-2" />
                +966 50 123 4567
              </p>
            </div>
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <Edit className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Financial Summary */}
        {userData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Wallet className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Total Balance</p>
                  <p className="text-xl font-bold text-green-600">
                    {formatCurrency(userData.totalBalance)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Building2 className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Connected Accounts</p>
                  <p className="text-xl font-bold text-blue-600">{userData.accountsCount}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <div className="text-purple-600 font-bold">%</div>
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Savings Rate</p>
                  <p className="text-xl font-bold text-purple-600">
                    {userData.savingsRate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Connected Banks */}
        {userData && userData.accounts.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Connected Banks</h3>
            <div className="space-y-3">
              {userData.accounts.map((account) => (
                <div key={account.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <Building2 className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{account.bank_name}</p>
                      <p className="text-sm text-gray-600">{account.account_name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-gray-900">
                      {formatCurrency(account.balance, account.currency)}
                    </p>
                    <p className="text-sm text-gray-600">{account.currency}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Settings */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 mb-6">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Settings</h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {/* Notifications */}
            <div className="p-6 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Bell className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="font-medium text-gray-900">Notifications</p>
                  <p className="text-sm text-gray-600">Receive alerts about your finances</p>
                </div>
              </div>
              <button
                onClick={() => setNotifications(!notifications)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications ? 'bg-green-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Language */}
            <div className="p-6 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Globe className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="font-medium text-gray-900">Language</p>
                  <p className="text-sm text-gray-600">العربية / English</p>
                </div>
              </div>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="both">Both</option>
              </select>
            </div>

            {/* Privacy & Security */}
            <div className="p-6">
              <div className="flex items-center space-x-3">
                <Shield className="h-5 w-5 text-gray-400" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Privacy & Security</p>
                  <p className="text-sm text-gray-600">Manage your data and security settings</p>
                </div>
                <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                  Manage
                </button>
              </div>
            </div>

            {/* Help & Support */}
            <div className="p-6">
              <div className="flex items-center space-x-3">
                <HelpCircle className="h-5 w-5 text-gray-400" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Help & Support</p>
                  <p className="text-sm text-gray-600">Get help with using Nama'aAI</p>
                </div>
                <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                  Contact
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <LogOut className="h-5 w-5" />
            <span>Logout</span>
          </button>
        </div>

        {/* App Info */}
        <div className="text-center mt-8 py-6">
          <p className="text-gray-500 text-sm">
            Nama'aAI | نَماء<br />
            Version 1.0.0<br />
            Your Intelligent Financial Advisor
          </p>
        </div>
      </div>
    </div>
  )
}