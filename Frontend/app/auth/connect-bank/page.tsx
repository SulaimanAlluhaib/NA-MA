'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Cookies from 'js-cookie'
import { Building2, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react'
import Image from 'next/image'

const API_BASE_URL = 'http://192.168.5.38:5000'

interface BankProvider {
  providerId: string
  name: string
  displayName: string
  logoUrl: string
  countryCode: string
  aisStatus: string
  pisStatus: string
}

export default function ConnectBankPage() {
  const [providers, setProviders] = useState<BankProvider[]>([])
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    loadProviders()
  }, [])

  const loadProviders = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/accounts/providers`)
      
      if (response.data.providers) {
        setProviders(response.data.providers)
      }
    } catch (error) {
      setError('Failed to load bank providers')
      console.error('Error loading providers:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleConnectBank = async () => {
    if (!selectedProvider) {
      setError('Please select a bank')
      return
    }

    const customerUserId = Cookies.get('customerUserId')
    const userEmail = Cookies.get('userEmail')

    if (!customerUserId || !userEmail) {
      router.push('/auth/register')
      return
    }

    setIsConnecting(true)
    setError('')

    try {
      const response = await axios.post(`${API_BASE_URL}/api/accounts/create-intent`, {
        customerUserId,
        firstName: 'User',
        lastName: 'Name',
        email: userEmail,
        redirectUrl: `${window.location.origin}/auth/callback`,
      })

      if (response.data) {
        // In a real implementation, you would redirect to the bank's login URL
        // For demo purposes, we'll simulate a successful connection
        setTimeout(() => {
          setIsConnecting(false)
          router.push('/')
        }, 2000)
      }
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to connect bank')
      setIsConnecting(false)
    }
  }

  const handleSkip = () => {
    router.push('/')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading bank providers...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => router.back()}
            className="mr-4 p-2 rounded-full hover:bg-white/20 transition-colors"
          >
            <ArrowLeft className="h-6 w-6 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Connect Your Bank</h1>
            <p className="text-gray-600">Choose your bank to get started with personalized insights</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <Building2 className="h-16 w-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Select Your Bank</h2>
            <p className="text-gray-600">
              We'll securely connect to your bank account to provide personalized financial insights
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Bank Selection */}
          <div className="space-y-3 mb-8">
            {providers.map((provider) => (
              <div
                key={provider.providerId}
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  selectedProvider === provider.providerId
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedProvider(provider.providerId)}
              >
                <div className="flex items-center">
                  <div className="flex-shrink-0 mr-4">
                    <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden">
                      {provider.logoUrl ? (
                        <Image
                          src={provider.logoUrl}
                          alt={provider.displayName}
                          width={48}
                          height={48}
                          className="object-contain"
                        />
                      ) : (
                        <Building2 className="h-6 w-6 text-gray-400" />
                      )}
                    </div>
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{provider.displayName}</h3>
                    <p className="text-sm text-gray-600">{provider.name}</p>
                    <div className="flex items-center mt-1">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        provider.aisStatus === 'AVAILABLE' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {provider.aisStatus === 'AVAILABLE' ? (
                          <>
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Available
                          </>
                        ) : (
                          'Unavailable'
                        )}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex-shrink-0">
                    <div className={`w-5 h-5 rounded-full border-2 ${
                      selectedProvider === provider.providerId
                        ? 'border-green-500 bg-green-500'
                        : 'border-gray-300'
                    }`}>
                      {selectedProvider === provider.providerId && (
                        <CheckCircle className="h-5 w-5 text-white" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            <button
              onClick={handleConnectBank}
              disabled={!selectedProvider || isConnecting}
              className="w-full btn-primary py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isConnecting ? (
                <>
                  <div className="spinner mr-2"></div>
                  Connecting to Bank...
                </>
              ) : (
                'Connect Bank Account'
              )}
            </button>
            
            <button
              onClick={handleSkip}
              className="w-full btn-secondary py-3 text-lg"
            >
              Skip for Now
            </button>
          </div>

          {/* Security Notice */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <CheckCircle className="h-5 w-5 text-blue-500 mt-0.5" />
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-blue-900">Secure Connection</h4>
                <p className="text-sm text-blue-700 mt-1">
                  Your banking credentials are encrypted and secure. We use bank-grade security 
                  and never store your login information.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Benefits */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/70 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">🔒</div>
            <h3 className="font-semibold text-gray-900 mb-1">Bank-Level Security</h3>
            <p className="text-sm text-gray-600">Your data is protected with enterprise-grade encryption</p>
          </div>
          
          <div className="bg-white/70 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-gray-900 mb-1">Smart Insights</h3>
            <p className="text-sm text-gray-600">Get AI-powered analysis of your spending patterns</p>
          </div>
          
          <div className="bg-white/70 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">💡</div>
            <h3 className="font-semibold text-gray-900 mb-1">Personalized Advice</h3>
            <p className="text-sm text-gray-600">Receive tailored financial recommendations</p>
          </div>
        </div>
      </div>
    </div>
  )
}