# fmnews-content

Free, GitHub-backed CMS for the FM News Android app.

The app fetches these JSON files from `raw.githubusercontent.com` on
every launch (and on pull-to-refresh). Edit a file here → app shows
the change within a minute. No server, no hosting bill.

## Files

| File | Powers | Update frequency |
|------|--------|------------------|
| `app-config.json` | global toggles (maintenance, ad on/off, feature flags) | rarely |
| `breaking.json` | scrolling "BREAKING" ticker on home top | as needed |
| `featured.json` | hero banner cards on home top | daily |
| `notifications.json` | push notification history shown in bell icon | per push |
| `epaper.json` | daily e-paper PDF links | daily |
| `tweets.json` | Twitter mirror, shown as text-news cards in feed | per tweet |
| `facebook.json` | Facebook photo posts, shown as "Photo News" cards | per post |
| `instagram.json` | Instagram reels mirror, shown in Shorts tab | per reel |

## How to update from your phone

1. Open `github.com/fmnews/fmnews-content` in any browser
2. Tap the file you want to edit
3. Tap the pencil ✏️ icon → edit JSON → "Commit changes"
4. Open the app and pull-to-refresh — change visible in ~30 seconds

## Schema rules

- Every file has a top-level `version` field (currently `1`). Bumping
  this signals a breaking change; the app falls back to defaults if
  it doesn't recognise the version.
- Dates are ISO-8601 UTC strings: `2026-05-30T10:00:00Z`.
- Items with `expiresAt` in the past are auto-hidden by the app.
- `lang` field can be `hi`, `en`, or `both`. `both` shows on either
  language setting.

## Safety

- Keep this repo **public** so `raw.githubusercontent.com` works
  without auth.
- Never put secrets, API keys, or personal data here. Anyone can
  read this content.
