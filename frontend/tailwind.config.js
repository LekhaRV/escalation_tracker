/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Professional Brand Palette - Deeper, more sophisticated
                brand: {
                    50: '#f0f4f8',
                    100: '#d9e2ec',
                    200: '#bcccdc',
                    300: '#9fb3c8',
                    400: '#829ab1',
                    500: '#627d98',
                    600: '#486581',
                    700: '#334e68', // Primary - Professional Navy
                    800: '#243b53',
                    900: '#102a43',
                    950: '#0a1929',
                },
                // Professional Status Colors - Refined, not neon
                status: {
                    success: '#059669', // Emerald-600
                    warning: '#d97706', // Amber-600
                    danger: '#dc2626',  // Red-600
                    info: '#2563eb',    // Blue-600
                },
                // Accent for highlights
                accent: {
                    DEFAULT: '#0ea5e9', // Sky-500 - Professional cyan
                    hover: '#0284c7',
                },
                // Surface colors
                app: '#f8fafc',      // Slate-50
                surface: '#ffffff',

                // Text colors
                logic: '#1e293b',    // Slate-800
                algo: '#475569',     // Slate-600
                muted: '#94a3b8',    // Slate-400

                // Standard slate
                slate: {
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#64748b',
                    600: '#475569',
                    700: '#334155',
                    800: '#1e293b',
                    900: '#0f172a',
                    950: '#020617',
                },
            },
            fontFamily: {
                sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            },
            boxShadow: {
                'soft': '0 2px 8px -2px rgba(0, 0, 0, 0.08)',
                'medium': '0 4px 12px -4px rgba(0, 0, 0, 0.12)',
            }
        },
    },
    plugins: [],
}
