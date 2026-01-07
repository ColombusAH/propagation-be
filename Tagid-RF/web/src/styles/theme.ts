/**
 * Modern Design System Theme
 * 
 * Professional color palette with excellent contrast and readability
 */

export const theme = {
  colors: {
    // Primary - Subtle Professional Blue
    primary: '#4F46E5',
    primaryDark: '#4338CA',
    primaryLight: '#6366F1',
    primaryGradient: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',

    // Accent Colors - Muted and Professional
    accent: {
      green: '#059669',
      greenDark: '#047857',
      orange: '#EA580C',
      orangeDark: '#C2410C',
      red: '#DC2626',
      redDark: '#B91C1C',
      blue: '#2563EB',
      blueDark: '#1D4ED8',
      purple: '#7C3AED',
      pink: '#DB2777',
    },

    // Semantic Colors
    success: '#059669',
    successLight: '#D1FAE5',
    successDark: '#047857',
    error: '#DC2626',
    errorLight: '#FEE2E2',
    errorDark: '#B91C1C',
    warning: '#EA580C',
    warningLight: '#FED7AA',
    warningDark: '#C2410C',
    info: '#2563EB',
    infoLight: '#DBEAFE',
    infoDark: '#1D4ED8',

    // Neutrals - Gray Scale with Better Contrast
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },

    // Backgrounds
    background: '#FFFFFF',
    backgroundAlt: '#F9FAFB',
    backgroundDark: '#1F2937',
    surface: '#FFFFFF',
    surfaceHover: '#F9FAFB',
    surfaceElevated: '#FFFFFF',

    // Text - High Contrast
    text: '#111827',
    textSecondary: '#4B5563',
    textLight: '#6B7280',
    textInverse: '#FFFFFF',
    textMuted: '#9CA3AF',

    // Borders
    border: '#E5E7EB',
    borderLight: '#F3F4F6',
    borderDark: '#D1D5DB',
    borderFocus: '#4F46E5',

    // Overlays
    overlay: 'rgba(17, 24, 39, 0.5)',
    overlayLight: 'rgba(17, 24, 39, 0.25)',
    overlayDark: 'rgba(17, 24, 39, 0.75)',

    // Glassmorphism - Subtle
    glass: 'rgba(255, 255, 255, 0.95)',
    glassDark: 'rgba(31, 41, 55, 0.95)',
  },

  spacing: {
    xs: '0.25rem',    // 4px
    sm: '0.5rem',     // 8px
    md: '1rem',       // 16px
    lg: '1.5rem',     // 24px
    xl: '2rem',       // 32px
    '2xl': '2.5rem',  // 40px
    '3xl': '3rem',    // 48px
    '4xl': '4rem',    // 64px
  },

  borderRadius: {
    none: '0',
    sm: '0.25rem',    // 4px
    md: '0.5rem',     // 8px
    lg: '0.75rem',    // 12px
    xl: '1rem',       // 16px
    '2xl': '1.5rem',  // 24px
    full: '9999px',
  },

  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',

    // Subtle colored shadows
    primarySm: '0 2px 8px rgba(79, 70, 229, 0.15)',
    primaryMd: '0 4px 16px rgba(79, 70, 229, 0.2)',
    primaryLg: '0 8px 24px rgba(79, 70, 229, 0.25)',
  },

  typography: {
    fontFamily: {
      base: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      heading: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      mono: "'Fira Code', 'Courier New', monospace",
    },
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
    },
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
    lineHeight: {
      none: '1',
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '2',
    },
  },

  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px',
    ultrawide: '1536px',
  },

  zIndex: {
    toast: 10000,
    modal: 1000,
    overlay: 900,
    dropdown: 800,
    sticky: 500,
    header: 100,
    base: 1,
    below: -1,
  },

  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: '500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  effects: {
    blur: {
      sm: 'blur(4px)',
      md: 'blur(8px)',
      lg: 'blur(16px)',
      xl: 'blur(24px)',
    },
    backdrop: 'blur(8px) saturate(150%)',
  },
} as const;

export type Theme = typeof theme;
