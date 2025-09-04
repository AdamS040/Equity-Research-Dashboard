import { useSkipLinks } from '../hooks/useAccessibility'

export const SkipLinks = () => {
  const skipLinks = useSkipLinks()

  return (
    <div className="sr-only focus-within:not-sr-only">
      {skipLinks.map((link) => (
        <a
          key={link.href}
          href={link.href}
          className="absolute top-0 left-0 z-50 bg-primary-600 text-white px-4 py-2 rounded-br-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          {link.text}
        </a>
      ))}
    </div>
  )
}
