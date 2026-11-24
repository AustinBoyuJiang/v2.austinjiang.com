# Personal website

This is a static website. Contact details and location are redacted, messaging is disabled, private resume downloads are removed, and no Google Maps API is loaded.

## Local development and publishing

1. Use Node.js 22 or later.
2. Run `npm run build` and publish only `dist/`. The build copies tracked website assets and excludes Git metadata, environment files and development tools. Environment credentials are not injected into browser scripts.
3. Push changes to the connected Git repository for the existing Cloudflare deployment. No contact form, mail handler, or Google API integration is included in the static output.
4. In each new clone run `git config core.hooksPath .githooks`. The hooks check credentials and the redacted contact surface. GitHub Actions repeats these checks.

Rewriting Git history does not remove cached old commit URLs or other people's copies. Cache removal requests require the hosting provider's review.
