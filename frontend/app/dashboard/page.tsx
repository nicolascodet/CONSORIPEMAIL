'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    emails: 0,
    attachments: 0,
    processed: 0
  })

  const [status, setStatus] = useState('processing') // 'processing' | 'complete' | 'error'

  useEffect(() => {
    // Simulate progress
    const timer = setInterval(() => {
      setStats(prev => ({
        emails: Math.min(prev.emails + 5, 127),
        attachments: Math.min(prev.attachments + 2, 43),
        processed: Math.min(prev.processed + 3, 43)
      }))
    }, 200)

    return () => clearInterval(timer)
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-8">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-4xl mx-auto space-y-12"
      >
        {/* Header */}
        <div className="space-y-2">
          <motion.h1 
            initial={{ y: 20 }}
            animate={{ y: 0 }}
            className="text-4xl font-bold tracking-tight"
          >
            Processing Inbox
          </motion.h1>
          <p className="text-gray-400">Analyzing your email data for insights</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-6">
          {[
            { label: 'Emails Found', value: stats.emails },
            { label: 'Attachments', value: stats.attachments },
            { label: 'Processed', value: stats.processed }
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6 relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-violet-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              <p className="text-gray-400 text-sm">{stat.label}</p>
              <p className="text-3xl font-bold mt-2">{stat.value}</p>
            </motion.div>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="space-y-4">
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(stats.processed / stats.attachments) * 100}%` }}
              className="h-full bg-gradient-to-r from-blue-500 to-violet-500"
            />
          </div>
          <p className="text-sm text-gray-400 text-center">
            {Math.round((stats.processed / stats.attachments) * 100)}% Complete
          </p>
        </div>

        {/* Recent Activity */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Recent Activity</h2>
          <div className="space-y-2">
            {[
              'Analyzing email patterns...',
              'Extracting text from attachments...',
              'Processing document contents...',
              'Generating insights...'
            ].map((activity, i) => (
              <motion.div
                key={activity}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center space-x-3 text-sm text-gray-400"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                <span>{activity}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </main>
  )
}
