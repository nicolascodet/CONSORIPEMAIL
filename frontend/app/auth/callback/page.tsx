'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function AuthCallback() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  useEffect(() => {
    const code = searchParams.get('code')
    const code_verifier = sessionStorage.getItem('code_verifier')
    
    if (!code) {
      console.error('No code received from Microsoft')
      router.push('/?error=no_code')
      return
    }

    if (!code_verifier) {
      console.error('No code verifier found in session storage')
      router.push('/?error=no_code_verifier')
      return
    }
    
    const exchangeCode = async () => {
      try {
        console.log('Received auth code, exchanging for tokens...')
        
        const response = await fetch(`http://localhost:8000/auth/microsoft/callback?code=${code}&code_verifier=${code_verifier}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        })
        
        if (!response.ok) {
          const error = await response.text()
          console.error('Failed to authenticate:', error)
          throw new Error(`Failed to authenticate: ${error}`)
        }
        
        const data = await response.json()
        console.log('Authentication successful:', data)
        
        // Clear code verifier from session storage
        sessionStorage.removeItem('code_verifier')
        
        // Redirect to dashboard
        router.push('/dashboard')
      } catch (error) {
        console.error('Authentication error:', error)
        router.push(`/?error=${encodeURIComponent(error.message)}`)
      }
    }
    
    exchangeCode()
  }, [router, searchParams])
  
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="flex flex-col items-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
        <h2 className="text-xl font-semibold">Connecting your account...</h2>
        <p className="text-gray-600">Please wait while we complete the authentication.</p>
      </div>
    </div>
  )
}
