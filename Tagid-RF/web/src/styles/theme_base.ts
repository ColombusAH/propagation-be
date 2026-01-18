export const theme = {
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
    sm: '4px',
    md: '6px',
    lg: '6px',
    xl: '8px',
    '2xl': '12px',
    full: '9999px',
  },

  shadows: {
    none: 'none',
    sm: '0 2px 6px rgba(15, 23, 42, 0.06)',
    md: '0 6px 16px rgba(15, 23, 42, 0.08)',
    lg: '0 10px 28px rgba(15, 23, 42, 0.12)',
    xl: '0 16px 40px rgba(15, 23, 42, 0.14)',
    '2xl': '0 24px 56px rgba(15, 23, 42, 0.16)',
    inner: 'inset 0 2px 4px rgba(15, 23, 42, 0.04)',
    glow: '0 0 20px rgba(30, 41, 59, 0.15)',
    focus: '0 0 0 3px rgba(30, 41, 59, 0.25)',
    primarySm: '0 4px 10px rgba(30, 41, 59, 0.15)',
    primaryMd: '0 6px 14px rgba(30, 41, 59, 0.2)',
    primaryLg: '0 10px 24px rgba(30, 41, 59, 0.25)',
  },

  typography: {
    fontFamily: {
      base: "'Heebo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      heading: "'Heebo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', 'Fira Code', monospace",
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem',    // 48px
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      none: 1,
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
  },

  transitions: {
    fast: '0.15s cubic-bezier(0.4, 0, 0.2, 1)',
    base: '0.25s cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    slower: '0.6s cubic-bezier(0.4, 0, 0.2, 1)',
  },

  animations: {
    fadeIn: 'fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    slideUp: 'slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
    scaleIn: 'scaleIn 0.3s cubic-bezier(0.4, 0, 0, 1)',
  },

  global: `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes scaleIn {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: scale(1); }
    }
    
    body {
      transition: background-color 0.3s ease, color 0.3s ease;
    }

    * {
      transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease, color 0.2s ease;
    }
  `,

  zIndex: {
    base: 1,
    dropdown: 100,
    header: 150,
    sticky: 200,
    modal: 300,
    popover: 400,
    tooltip: 500,
    toast: 600,
  },

  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px',
    ultrawide: '1536px',
  },
};