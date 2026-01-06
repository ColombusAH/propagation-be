# Scan & Pay App

A React Native app with Expo Router for scanning barcodes/QR codes and processing payments with Stripe.

## Features

- 📷 **Scan Tab**: Camera-based barcode/QR code scanning
- 🛒 **Cart Tab**: Shopping cart with quantity controls
- 💳 **Payment**: Stripe integration for secure payments

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Stripe Keys

1. Get your Stripe keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Create a `.env` file in the root directory:

```bash
# Copy the example file
cp server.env.example .env
```

3. Edit `.env` and add your Stripe keys:

```env
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
PORT=3002
NODE_ENV=development
```

### 3. Update App Configuration

Update `app.json` with your Stripe publishable key:

```json
{
  "extra": {
    "EXPO_PUBLIC_API_URL": "http://localhost:3002",
    "EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY": "pk_test_your_publishable_key_here"
  }
}
```

## Running the App

### Option 1: MVP Mode (No Backend Required)

The app is configured to run in MVP mode by default, which means:
- ✅ No backend server needed
- ✅ Mock payment simulation
- ✅ Perfect for demos and testing
- ✅ Easy to switch to production later

```bash
npm start
```

### Option 2: Full Production Mode

**Terminal 1 - Backend Server:**
```bash
npm run server:dev
```

**Terminal 2 - Expo App:**
```bash
npm start
```

### Option 3: Run Everything Together

```bash
npm run dev
```

This will start both the backend server and the Expo development server.

## Available Scripts

- `npm start` - Start Expo app (MVP mode)
- `npm run dev` - Start both backend and frontend
- `npm run server` - Start backend server once
- `npm run server:dev` - Start backend server with auto-reload
- `npm run test:backend` - Test if backend is working
- `npm run android` - Run on Android
- `npm run ios` - Run on iOS
- `npm run web` - Run on web

## Switching Between MVP and Production Modes

### MVP Mode (Default)
- No backend server required
- Mock payment simulation
- Perfect for demos and testing

To enable MVP mode, edit `src/config/payment.ts`:
```typescript
export const PAYMENT_CONFIG = {
  MVP_MODE: true, // Set to true for MVP
  // ... other config
}
```

### Production Mode
- Requires backend server running
- Real Stripe payments
- Full payment processing

To enable production mode, edit `src/config/payment.ts`:
```typescript
export const PAYMENT_CONFIG = {
  MVP_MODE: false, // Set to false for production
  // ... other config
}
```

## Testing the Backend

Once the server is running, you can test it:

```bash
# Test backend connection
npm run test:backend

# Manual health check
curl http://localhost:3002/health

# Test payment intent creation
curl -X POST http://localhost:3002/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{"items":[{"id":"test","priceInCents":1000,"qty":1}],"currency":"usd"}'
```

## Product Catalog

The app includes a hardcoded product catalog for testing:

- `7290001234567` → Milk 1L ($5.90)
- `QR:COFFEE-250` → Coffee 250g ($18.90)

## Troubleshooting

### Backend Issues

1. **"STRIPE_SECRET_KEY is not set"**: Make sure you created a `.env` file with your Stripe secret key
2. **Port already in use**: Change the PORT in `.env` or kill the process using port 3002
3. **Stripe errors**: Verify your Stripe keys are correct and you're using test keys for development

### Frontend Issues

1. **Camera permission denied**: Grant camera permissions in your device settings
2. **Navigation errors**: Make sure you're using the correct Expo Router navigation methods
3. **Import errors**: Check that all import paths use the `@/` alias correctly

## Project Structure

```
├── app/                 # Expo Router pages
│   ├── (tabs)/         # Tab navigation
│   └── pay.tsx         # Payment modal
├── src/
│   ├── screens/        # Screen components
│   └── store/          # Zustand state management
├── server/             # Backend API
└── components/         # Shared components
```
