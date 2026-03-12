/**
 * Central registry of all HelpIcon feature keys used in the app.
 *
 * HOW TO ADD A NEW HELP ICON:
 * 1. Add an entry here (key, label, location, hint).
 * 2. Drop <HelpIcon feature="your.key" /> into the relevant Vue template.
 * 3. Go to Admin → Help Links and create a matching entry for that key.
 *
 * The admin panel reads this registry to show a dropdown of known keys
 * so you never have to guess what string to type.
 */

export const HELP_FEATURE_KEYS = [
  {
    key: 'import.upload',
    label: 'Import — Upload',
    location: 'Import Content page (header)',
    hint: 'Explains the import tool and supported file types.',
  },
  {
    key: 'publish.dashboard',
    label: 'Publication Dashboard',
    location: 'Publication Dashboard (header)',
    hint: 'Overview of publications, exporting PDFs and mobile knowledge bases.',
  },
  {
    key: 'reviews.dashboard',
    label: 'Reviews Dashboard',
    location: 'Reviews Dashboard (header)',
    hint: 'Explains the review workflow: requesting reviews, tokens, and feedback.',
  },
]

/** Quick lookup: key → registry entry */
export const HELP_KEY_MAP = Object.fromEntries(
  HELP_FEATURE_KEYS.map(e => [e.key, e])
)
