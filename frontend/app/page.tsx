'use client'

import { motion } from 'framer-motion'

const features = [
  {
    title: 'Fast',
    description: 'Process thousands of emails in minutes',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    )
  },
  {
    title: 'Secure',
    description: 'Your data never leaves your control',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    )
  },
  {
    title: 'Simple',
    description: 'Connect and analyze in minutes',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    )
  }
]

export default function Home() {
  const handleConnect = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/microsoft', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Auth URL response:', data);

      // Store code verifier in session storage
      if (data.code_verifier) {
        sessionStorage.setItem('code_verifier', data.code_verifier);
      }
      
      // Redirect to Microsoft login
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        throw new Error('No auth_url in response');
      }
    } catch (error) {
      console.error('Failed to get auth URL:', error);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-md w-full space-y-12 text-center"
      >
        <div className="space-y-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="relative w-24 h-24 mx-auto"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-violet-500 rounded-xl blur-xl opacity-50" />
            <div className="relative bg-black rounded-xl p-6">
              <svg className="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </motion.div>
          
          <h1 className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
            Email Analyzer
          </h1>
          <p className="text-gray-400 text-lg">
            Transform your inbox into insights
          </p>
        </div>

        <motion.button
          onClick={handleConnect}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="group relative w-full px-8 py-4 overflow-hidden rounded-lg font-medium tracking-wide text-white"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-violet-500" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <span className="relative">Connect Outlook</span>
        </motion.button>

        <div className="grid grid-cols-1 gap-6 pt-12">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.1 + 0.5 }}
              className="flex items-center space-x-4 p-4 rounded-lg bg-white/5 backdrop-blur-sm group hover:bg-white/10 transition-colors"
            >
              <div className="flex-shrink-0 p-2 rounded-lg bg-gradient-to-r from-blue-500/10 to-violet-500/10 text-blue-400 group-hover:text-blue-300 transition-colors">
                {feature.icon}
              </div>
              <div className="flex-1 text-left">
                <h3 className="font-medium text-white">{feature.title}</h3>
                <p className="text-sm text-gray-400">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </main>
  )
}
