interface Props {
  currentLanguage: string
  onLanguageChange: (lang: string) => void
}

const LANGUAGES = [
  { code: 'en', label: '🇬🇧 English' },
  { code: 'fr', label: '🇫🇷 Français' },
  { code: 'vi', label: '🇻🇳 Tiếng Việt' },
]

export default function LanguageSelector({ currentLanguage, onLanguageChange }: Props) {
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => onLanguageChange(lang.code)}
          style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: '6px', backgroundColor: currentLanguage === lang.code ? '#007bff' : 'white', color: currentLanguage === lang.code ? 'white' : '#333', cursor: 'pointer', fontWeight: currentLanguage === lang.code ? 'bold' : 'normal' }}
        >
          {lang.label}
        </button>
      ))}
    </div>
  )
}
