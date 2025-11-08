import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Claims Guardian AI - Medical Claims Validator',
  description: 'AI-powered medical claims validation with multi-agent system',
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
