import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
export default defineConfig({
  base: process.env.GITHUB_PAGES === 'true' ? `/${process.env.GITHUB_REPOSITORY?.split('/')[1] ?? 'research-funding-radar'}/` : '/',
  plugins: [react(), VitePWA({registerType:'autoUpdate',includeAssets:['icon.svg'],manifest:{name:'Research Funding Radar',short_name:'Funding Radar',description:'Research funding opportunities matched to high-temperature industrial research',theme_color:'#142a42',background_color:'#f4f7fb',display:'standalone',icons:[{src:'icon.svg',sizes:'any',type:'image/svg+xml',purpose:'any'}]}})]
});
