import { defineConfig } from 'astro/config'

export default defineConfig({
  site: 'https://willrowe.net/online-cv',
  srcDir: 'src',
  // Serve static files from `public/` (create this folder locally).
  publicDir: 'public',
  outDir: 'dist',
})
