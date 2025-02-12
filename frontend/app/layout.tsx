import './globals.css'
import { Inter } from 'next/font/google'
import NavBar from '../components/nav-bar'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Email Analyzer',
  description: 'A minimalist email analysis tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-black text-white min-h-screen antialiased`}>
        <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-gray-900/20 to-gray-900/30 pointer-events-none" />
        <div className="relative">
          <NavBar />
          {children}
        </div>
      </body>
    </html>
  )
}
