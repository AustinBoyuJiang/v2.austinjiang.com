import { cp, mkdir, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(root, 'dist');
const dotenv = resolve(root, '.env');
if (existsSync(dotenv)) process.loadEnvFile(dotenv);
const key = (process.env.GOOGLE_MAPS_API_KEY || '').trim();
if (key && !/^AIza[0-9A-Za-z_-]{35}$/.test(key)) {
  throw new Error('GOOGLE_MAPS_API_KEY must be empty or a valid, website-restricted browser key.');
}

// Only tracked website assets enter the public directory. Dotenv files, Git
// metadata, development tools and local server configuration are never copied.
const files = execFileSync('git', ['ls-files', '-z'], { cwd: root }).toString().split('\0').filter(Boolean);
await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
for (const file of files) {
  if (!(/\.html$/.test(file) || /^(css|js|img|profile|projects|blog)\//.test(file))) continue;
  const destination = resolve(output, file);
  await mkdir(dirname(destination), { recursive: true });
  await cp(resolve(root, file), destination);
}
await mkdir(resolve(output, 'js'), { recursive: true });
await writeFile(resolve(output, 'js/maps-config.js'), `window.AUSTIN_GOOGLE_MAPS_API_KEY = ${JSON.stringify(key)};\n`);
console.log(key ? 'Built dist/ with the configured public browser Maps key.' : 'Built dist/ with a map link; no paid Maps API is loaded.');
