import './globals.css'
import type { Metadata } from 'next'
import { Inter, Cairo } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })
const cairo = Cairo({ subsets: ['arabic', 'latin'] })

export const metadata: Metadata = {
  title: "Nama'aAI | نَماء - Intelligent Financial Advisor",
  description: 'AI-powered financial advisor for Saudi Arabian users',
  keywords: ['finance', 'AI', 'Saudi Arabia', 'banking', 'investment'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" dir="ltr">
      <body className={`${inter.className} ${cairo.className} antialiased`}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
      </body>
    </html>
  )
}