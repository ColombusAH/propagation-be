// src/config/payment.ts
// Payment Configuration - Easy to switch between MVP and Production

export const PAYMENT_CONFIG = {
  // Set to true for MVP/demo mode, false for production
  MVP_MODE: true,
  
  // API Configuration
  API_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:3002',
  
  // Stripe Configuration
  STRIPE_PUBLISHABLE_KEY: process.env.EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_...',
  
  // Return URL for Stripe (required for iOS redirects)
  RETURN_URL: 'scanandpay://stripe-redirect',
  
  // MVP Mock Data
  MOCK_PAYMENT_DATA: {
    clientSecret: "pi_mock_client_secret_for_testing",
    amount: 0,
    currency: "usd"
  },
  
  // Merchant Display Name
  MERCHANT_NAME: 'Scan & Pay Demo',
  
  // Debug Settings
  DEBUG_MODE: __DEV__, // Automatically true in development
}

// Helper function to check if we're in MVP mode
export const isMVPMode = () => PAYMENT_CONFIG.MVP_MODE

// Helper function to get API URL
export const getAPIUrl = () => PAYMENT_CONFIG.API_URL

// Helper function to get Stripe key
export const getStripeKey = () => PAYMENT_CONFIG.STRIPE_PUBLISHABLE_KEY

// Helper function to get return URL
export const getReturnUrl = () => PAYMENT_CONFIG.RETURN_URL
