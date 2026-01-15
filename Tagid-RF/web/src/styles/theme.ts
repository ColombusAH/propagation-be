/**
 * Titanium White Enterprise Design System
 * 
 * Professional light palette with Heebo typography for Hebrew-first RTL interface
 * RFID Management System - Enterprise Grade
 */

import { theme as themeBase } from './theme_base';

export const lightTheme = {
  colors: {
    // Primary - Vibrant Royal Blue
    primary: '#2563EB',
    primaryDark: '#1E40AF',
    primaryLight: '#60A5FA',
    primaryGradient: 'linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)',

    // Semantic Colors - Professional Signal Palette
    success: '#10B981',
    successLight: '#D1FAE5',
    successDark: '#059669',
    error: '#EF4444',
    errorLight: '#FEE2E2',
    errorDark: '#DC2626',
    warning: '#F59E0B',
    warningLight: '#FEF3C7',
    warningDark: '#D97706',
    info: '#3B82F6',
    infoLight: '#DBEAFE',
    infoDark: '#2563EB',

    // Neutrals - Slate Scale
    gray: {
      50: '#F8FAFD',
      100: '#F1F5FB',
      200: '#E1E8F0',
      300: '#C4CFDA',
      400: '#9AAFC2',
      500: '#6B7A8C',
      600: '#475569',
      700: '#334155',
      800: '#1E293B',
      900: '#1C2833',
    },

    // Backgrounds - Clean White with Blue Tint
    background: '#F0F7FF',
    backgroundAlt: '#E6F0FF',
    backgroundDark: '#D1E5FF',
    surface: '#FFFFFF',
    surfaceHover: '#F0F9FF',
    surfaceElevated: '#FFFFFF',

    // Text - Professional Deep Blue
    text: '#1E293B',
    textSecondary: '#334155',
    textLight: '#475569',
    textInverse: '#FFFFFF',
    textMuted: '#64748B',

    // Borders
    border: '#DAE1E9',
    borderLight: '#E1E8F0',
    borderDark: '#C4CFDA',
    borderFocus: '#1F4E79',

    // Overlays
    overlay: 'rgba(15, 23, 42, 0.35)',
    overlayLight: 'rgba(15, 23, 42, 0.2)',
    overlayDark: 'rgba(15, 23, 42, 0.5)',

    // Glass effects
    glass: 'rgba(255, 255, 255, 0.95)',
    glassDark: 'rgba(255, 255, 255, 0.98)',

    // Role Badge Colors
    roles: {
      superAdmin: '#EF4444',
      networkAdmin: '#8B5CF6',
      storeManager: '#3B82F6',
      seller: '#10B981',
      customer: '#6B7280',
    },

    // Dark panel for special sections
    darkPanel: '#1E293B',
    darkPanelLight: '#334155',
  },
  spacing: themeBase.spacing,
  borderRadius: themeBase.borderRadius,
  shadows: themeBase.shadows,
  typography: themeBase.typography,
  transitions: themeBase.transitions,
  animations: themeBase.animations,
  global: themeBase.global,
  zIndex: themeBase.zIndex,
  breakpoints: themeBase.breakpoints,
};

export const darkTheme = {
  colors: {
    // Primary - Vibrant Royal Blue
    primary: '#3B82F6',
    primaryDark: '#2563EB',
    primaryLight: '#60A5FA',
    primaryGradient: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',

    // Semantic Colors
    success: '#10B981',
    successLight: '#064E3B',
    successDark: '#34D399',
    error: '#EF4444',
    errorLight: '#7F1D1D',
    errorDark: '#F87171',
    warning: '#F59E0B',
    warningLight: '#78350F',
    warningDark: '#FBBF24',
    info: '#3B82F6',
    infoLight: '#1E3A8A',
    infoDark: '#60A5FA',

    // Neutrals
    gray: {
      50: '#0F172A',
      100: '#1E293B',
      200: '#334155',
      300: '#475569',
      400: '#64748B',
      500: '#94A3B8',
      600: '#CBD5E1',
      700: '#E2E8F0',
      800: '#F1F5F9',
      900: '#F8FAFC',
    },

    // Backgrounds
    background: '#0F172A',
    backgroundAlt: '#1E293B',
    backgroundDark: '#020617',
    surface: '#1E293B',
    surfaceHover: '#334155',
    surfaceElevated: '#1E293B',

    // Text
    text: '#F8FAFC',
    textSecondary: '#CBD5E1',
    textLight: '#94A3B8',
    textInverse: '#0F172A',
    textMuted: '#64748B',

    // Borders
    border: '#334155',
    borderLight: '#1E293B',
    borderDark: '#475569',
    borderFocus: '#3B82F6',

    // Overlays
    overlay: 'rgba(0, 0, 0, 0.7)',
    overlayLight: 'rgba(0, 0, 0, 0.4)',
    overlayDark: 'rgba(0, 0, 0, 0.9)',

    // Glass effects
    glass: 'rgba(15, 23, 42, 0.8)',
    glassDark: 'rgba(15, 23, 42, 0.95)',

    // Role Badge Colors
    roles: {
      superAdmin: '#F87171',
      networkAdmin: '#A78BFA',
      storeManager: '#60A5FA',
      seller: '#34D399',
      customer: '#94A3B8',
    },

    // Dark panel for special sections
    darkPanel: '#020617',
    darkPanelLight: '#0F172A',
  },
  spacing: themeBase.spacing,
  borderRadius: themeBase.borderRadius,
  shadows: {
    ...themeBase.shadows,
    sm: '0 2px 6px rgba(0, 0, 0, 0.3)',
    md: '0 6px 16px rgba(0, 0, 0, 0.4)',
    lg: '0 10px 28px rgba(0, 0, 0, 0.5)',
  },
  typography: themeBase.typography,
  transitions: themeBase.transitions,
  animations: themeBase.animations,
  global: themeBase.global,
  zIndex: themeBase.zIndex,
  breakpoints: themeBase.breakpoints,
};

export const theme = lightTheme;

export type Theme = typeof theme;
