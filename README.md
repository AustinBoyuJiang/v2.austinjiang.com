# austinjiang.com
 My personal website

Click the [link](https://austinjiang.com)

## Local configuration and publishing

1. Use Node.js 22 or later. Copy `.env.example` to `.env`.
2. The default empty `GOOGLE_MAPS_API_KEY` uses a normal Google Maps link and makes no paid Maps API requests.
3. If an interactive map is needed, create a new browser-only key restricted to your exact website domains and the Maps JavaScript API; set it in the local `.env`. A browser map key remains visible to website visitors even when supplied through `.env`. Never use a server or Gemini key here.
4. Run `npm run build` and publish **only `dist/`**. Never serve the repository root or `.env` files. The build copies tracked website assets, not private environment files.
5. In every new clone run `git config core.hooksPath .githooks`. The pre-commit hook rejects tracked dotenv files and credential literals; pre-push scans all reachable history. GitHub Actions repeats the scan.

The old public credentials have been removed from this repository's reachable history. Rotate/revoke all previously exposed credentials; rewriting history cannot erase copies already downloaded or cached elsewhere.
