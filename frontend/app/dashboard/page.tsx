'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

interface Mailbox {
  id: number
  name: string
  type: string
  total_messages: number
  processed_messages: number
  last_processed: string
}

interface DashboardStats {
  totalEmails: number
  totalAttachments: number
  processedAttachments: number
  organizations: number
  contacts: number
}

export default function Dashboard() {
  const [mailboxes, setMailboxes] = useState<Mailbox[]>([])
  const [stats, setStats] = useState<DashboardStats>({
    totalEmails: 0,
    totalAttachments: 0,
    processedAttachments: 0,
    organizations: 0,
    contacts: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch mailboxes
        const mailboxesResponse = await fetch('http://localhost:8000/mailboxes')
        if (!mailboxesResponse.ok) throw new Error('Failed to fetch mailboxes')
        const mailboxesData = await mailboxesResponse.json()
        setMailboxes(mailboxesData)

        // Calculate total emails from mailboxes
        const totalEmails = mailboxesData.reduce((sum: number, mailbox: Mailbox) => sum + mailbox.total_messages, 0)

        // Fetch organizations
        const orgsResponse = await fetch('http://localhost:8000/organizations')
        if (!orgsResponse.ok) throw new Error('Failed to fetch organizations')
        const orgsData = await orgsResponse.json()

        // Fetch contacts
        const contactsResponse = await fetch('http://localhost:8000/contacts')
        if (!contactsResponse.ok) throw new Error('Failed to fetch contacts')
        const contactsData = await contactsResponse.json()

        setStats({
          totalEmails,
          totalAttachments: 0, // Will be updated from attachment processing
          processedAttachments: 0,
          organizations: orgsData.length,
          contacts: contactsData.length
        })

        // Start attachment processing
        const processResponse = await fetch('http://localhost:8000/process-attachments', {
          method: 'POST'
        })
        if (!processResponse.ok) throw new Error('Failed to start attachment processing')
        const processData = await processResponse.json()

        setStats(prev => ({
          ...prev,
          totalAttachments: processData.total || 0,
          processedAttachments: processData.processed || 0
        }))

      } catch (err) {
        console.error('Error fetching data:', err)
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-8 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xl text-gray-400"
        >
          Loading...
        </motion.div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-8 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xl text-red-400"
        >
          {error}
        </motion.div>
      </main>
    )
  }

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
            Email Analysis Dashboard
          </motion.h1>
          <p className="text-gray-400">Analyzing your email data for insights</p>
        </div>

        {/* Mailboxes */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Processed Mailboxes</h2>
          <div className="grid gap-4">
            {mailboxes.map((mailbox) => (
              <motion.div
                key={mailbox.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/5 backdrop-blur-sm rounded-xl p-6 relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-violet-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{mailbox.name}</h3>
                    <p className="text-sm text-gray-400">Type: {mailbox.type}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Messages: {mailbox.total_messages}</p>
                    <p className="text-sm text-gray-400">
                      Processed: {mailbox.processed_messages}
                    </p>
                  </div>
                </div>
                <div className="mt-4 h-1 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(mailbox.processed_messages / mailbox.total_messages) * 100}%` }}
                    className="h-full bg-gradient-to-r from-blue-500 to-violet-500"
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-6">
          {[
            { label: 'Total Emails', value: stats.totalEmails },
            { label: 'Organizations', value: stats.organizations },
            { label: 'Contacts', value: stats.contacts }
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

        {/* Attachment Processing */}
        {stats.totalAttachments > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Attachment Processing</h2>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(stats.processedAttachments / stats.totalAttachments) * 100}%` }}
                className="h-full bg-gradient-to-r from-blue-500 to-violet-500"
              />
            </div>
            <p className="text-sm text-gray-400 text-center">
              {stats.processedAttachments} of {stats.totalAttachments} attachments processed
            </p>
          </div>
        )}

        {/* Recent Activity */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Processing Steps</h2>
          <div className="space-y-2">
            {[
              { text: 'Importing emails from files...', done: true },
              { text: 'Extracting contacts and organizations...', done: stats.contacts > 0 },
              { text: 'Processing attachments...', done: stats.processedAttachments === stats.totalAttachments },
              { text: 'Generating insights...', done: false }
            ].map((activity, i) => (
              <motion.div
                key={activity.text}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center space-x-3 text-sm"
              >
                <div className={`w-1.5 h-1.5 rounded-full ${activity.done ? 'bg-green-500' : 'bg-blue-500'}`} />
                <span className={activity.done ? 'text-gray-300' : 'text-gray-400'}>
                  {activity.text}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </main>
  )
}
