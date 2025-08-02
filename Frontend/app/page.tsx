'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Cookies from 'js-cookie'
import axios from 'axios'
import { 
  Wallet, 
  TrendingUp, 
  MessageCircle, 
  User, 
  RefreshCw,
  PieChart,
  DollarSign,
  CreditCard,
  Building2
} from 'lucide-react'
import { PieChart as RechartsPieChart, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import Link from 'next/link'

interface Account {
  id: string
  account_name: string
  bank_name: string
  balance: number
  currency: string
}

interface CategorySpending {
  category: string
  amount: number
  count: number
  percentage: number
}

interface DashboardData {
  totalBalance: number
  accountsCount: number
  accounts: Account[]
  monthlyIncome: number
  monthlySpending: number
  savingsRate: number
  categorySpending: CategorySpending[]
  recentTransactions: any[]
}

const API_BASE_URL = 'http://192.168.5.38:5000'

const COLORS = ['#2E7D32', '#4CAF50', '#66BB6A', '#81C784', '#A5D6A7', '#C8E6C9']

export default function HomePage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [selectedAccount, setSelectedAccount] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const userId = Cookies.get('userId')
    if (!userId) {
      router.push('/auth/register')
      return
    }
    loadDashboardData(userId)
  }, [router])

  const loadDashboardData = async (userId: string) => {
    try {
      setIsLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/insights/dashboard/${userId}`)
      setDashboardData(response.data)
      
      if (response.data.accounts.length > 0 && !selectedAccount) {
        setSelectedAccount(response.data.accounts[0].id)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = async () => {
    const userId = Cookies.get('userId')
    if (!userId) return

    setIsRefreshing(true)
    await loadDashboardData(userId)
    setIsRefreshing(false)
  }

  const showAlternatives = async (category: string) => {
    const userId = Cookies.get('userId')
    if (!userId) return

    try {
      const response = await axios.get(`${API_BASE_URL}/api/insights/alternatives/${category}?user_id=${userId}`)
      
      // Create modal or alert with alternatives
      const alternatives = response.data.alternatives
      const alternativesText = alternatives.map((alt: any) => 
        `• ${alt.name}: ${alt.description_en} (Save ${alt.estimated_savings_percent}%)`
      ).join('\n')
      
      alert(`Alternatives for ${category}:\n\n${alternativesText}`)
    } catch (error) {
      console.error('Failed to load alternatives:', error)
    }
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your financial dashboard...</p>
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load dashboard data</p>
          <button onClick={handleRefresh} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  const pieChartData = dashboardData.categorySpending.slice(0, 6).map((item, index) => ({
    name: item.category,
    value: item.amount,
    color: COLORS[index % COLORS.length]
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="gradient-primary text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Wallet className="h-8 w-8" />
              <div>
                <h1 className="text-xl font-bold">Nama'aAI</h1>
                <p className="text-sm opacity-90">نَماء</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="p-2 rounded-full hover:bg-white/10 transition-colors"
              >
                <RefreshCw className={`h-5 w-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
              
              <Link href="/profile" className="p-2 rounded-full hover:bg-white/10 transition-colors">
                <User className="h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Balance Card */}
        <div className="card mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-2">Total Balance</p>
              <h2 className="text-3xl font-bold text-green-700 mb-4">
                {formatCurrency(dashboardData.totalBalance)}
              </h2>
            </div>
            
            <div className="md:w-1/3">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Account
              </label>
              <select
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
                className="input-field"
              >
                <option value="">All Accounts</option>
                {dashboardData.accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.bank_name} - {account.account_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Account Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
            {dashboardData.accounts.map((account) => (
              <div key={account.id} className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border">
                <div className="flex items-center justify-between mb-2">
                  <Building2 className="h-5 w-5 text-green-600" />
                  <span className="text-xs text-green-600 font-medium">{account.currency}</span>
                </div>
                <h3 className="font-semibold text-gray-800">{account.bank_name}</h3>
                <p className="text-sm text-gray-600 mb-2">{account.account_name}</p>
                <p className="text-lg font-bold text-green-700">
                  {formatCurrency(account.balance, account.currency)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Monthly Income</p>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(dashboardData.monthlyIncome)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-red-100">
                <DollarSign className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Monthly Spending</p>
                <p className="text-xl font-bold text-red-600">
                  {formatCurrency(dashboardData.monthlySpending)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100">
                <PieChart className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Savings Rate</p>
                <p className="text-xl font-bold text-blue-600">
                  {dashboardData.savingsRate.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Spending Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Pie Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Spending by Category</h3>
            {pieChartData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <RechartsPieChart data={pieChartData}>
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </RechartsPieChart>
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No spending data available
              </div>
            )}
          </div>
          
          {/* Category List */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Top Spending Categories</h3>
            <div className="space-y-3">
              {dashboardData.categorySpending.slice(0, 6).map((item, index) => (
                <div
                  key={item.category}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                  onClick={() => showAlternatives(item.category)}
                >
                  <div className="flex items-center">
                    <div
                      className="w-4 h-4 rounded-full mr-3"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <div>
                      <p className="font-medium">{item.category}</p>
                      <p className="text-sm text-gray-600">{item.count} transactions</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatCurrency(item.amount)}</p>
                    <p className="text-sm text-gray-600">{item.percentage.toFixed(1)}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link href="/chat" className="card-hover text-center">
            <MessageCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Ask AI Advisor</h3>
            <p className="text-gray-600">Get personalized financial advice in Arabic or English</p>
          </Link>
          
          <div 
            className="card-hover text-center cursor-pointer"
            onClick={() => {
              const userId = Cookies.get('userId')
              if (userId) {
                router.push('/investment?userId=' + userId)
              }
            }}
          >
            <TrendingUp className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Investment Advice</h3>
            <p className="text-gray-600">Discover Sharia-compliant investment opportunities</p>
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
        <div className="flex justify-around">
          <button className="flex flex-col items-center py-2 px-4 text-green-600">
            <Wallet className="h-5 w-5 mb-1" />
            <span className="text-xs">Home</span>
          </button>
          
          <Link href="/chat" className="flex flex-col items-center py-2 px-4 text-gray-600 hover:text-green-600">
            <MessageCircle className="h-5 w-5 mb-1" />
            <span className="text-xs">Chat</span>
          </Link>
          
          <Link href="/profile" className="flex flex-col items-center py-2 px-4 text-gray-600 hover:text-green-600">
            <User className="h-5 w-5 mb-1" />
            <span className="text-xs">Profile</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}