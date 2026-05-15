import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    base: '/skincare-webapp/',  // ชื่อ repo บน GitHub
})