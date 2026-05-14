'use client'

import { useState } from 'react'
import styles from './LanguageSelector.module.css'

interface LanguageSelectorProps {
  currentLanguage: string
  onLanguageChange: (language: string) => void
}

const languages = [
  { code: 'en', name: '🇬🇧 English' },
  { code: 'fr', name: '🇫🇷 Français' },
  { code: 'vi', name: '🇻🇳 Tiếng Việt' },
]

export default function LanguageSelector({
  currentLanguage,
  onLanguageChange,
}: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  const currentLang = languages.find((l) => l.code === currentLanguage) || languages[0]

  return (
    <div className={styles.container}>
      <button
        className={styles.trigger}
        onClick={() => setIsOpen(!isOpen)}
        title="Change language"
      >
        {currentLang.name}
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          {languages.map((lang) => (
            <button
              key={lang.code}
              className={`${styles.option} ${
                currentLanguage === lang.code ? styles.active : ''
              }`}
              onClick={() => {
                onLanguageChange(lang.code)
                setIsOpen(false)
              }}
            >
              {lang.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
