import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Lenoir Chatbot',
  description: 'Personal AI assistant with memory and voice capabilities',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
