# Scan & Pay Web App

A production-ready React + TypeScript web application that enables shoppers to scan product barcodes using their device camera, add items to cart, and complete purchases through a simple in-app payment flow. Works seamlessly on both desktop and mobile browsers.

## 🚀 Features

- **📷 Barcode Scanning**: Real-time camera barcode/QR code scanning using `@zxing/browser`
- **📱 Mobile-First Design**: Responsive, accessible UI built with styled-components
- **🛒 Shopping Cart**: Full cart management with quantity controls and persistence
- **💳 Simple Checkout**: In-app payment simulation (no external gateway)
- **📦 Product Catalog**: Browse and search products by name, SKU, or barcode
- **📋 Order History**: View past orders with complete details
- **💾 Offline Persistence**: Cart and orders saved to localStorage
- **♿ Accessible**: ARIA labels, keyboard navigation, and screen reader support
- **🎨 Modern UI**: Clean, minimal design with smooth transitions

## 🛠 Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand with localStorage persistence
- **Routing**: React Router v6
- **Styling**: styled-components with custom theme
- **Barcode Scanning**: @zxing/browser (HTML5 camera API)
- **Testing**: Vitest + React Testing Library
- **Linting**: ESLint + Prettier

## 📁 Project Structure

```
scan-and-pay-web/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── public/
│   └── icons/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── app.routes.tsx
│   ├── styles/
│   │   ├── global.ts
│   │   └── theme.ts
│   ├── lib/
│   │   ├── barcode/
│   │   │   └── BarcodeScanner.ts
│   │   ├── pwa/
│   │   │   └── registerSW.ts
│   │   └── utils/
│   │       ├── currency.ts
│   │       └── uuid.ts
│   ├── data/
│   │   └── products.json
│   ├── store/
│   │   ├── index.ts
│   │   ├── types.ts
│   │   └── slices/
│   │       ├── cartSlice.ts
│   │       ├── catalogSlice.ts
│   │       └── ordersSlice.ts
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── TopBar.tsx
│   │   ├── CameraView.tsx
│   │   ├── ProductCard.tsx
│   │   ├── QuantityInput.tsx
│   │   └── EmptyState.tsx
│   ├── pages/
│   │   ├── ScanPage.tsx
│   │   ├── CatalogPage.tsx
│   │   ├── CartPage.tsx
│   │   ├── CheckoutPage.tsx
│   │   ├── OrderSuccessPage.tsx
│   │   └── OrdersPage.tsx
│   ├── payment/
│   │   ├── SimplePaymentProvider.ts
│   │   └── types.ts
│   └── test/
│       └── setup.ts
└── README.md
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- HTTPS connection or localhost (required for camera access)

### Installation

```bash
# Clone or navigate to the project directory
cd scan-and-pay-web

# Install dependencies
npm install
# or
yarn install
```

### Development

```bash
# Start development server (runs on http://localhost:3000)
npm run dev
# or
yarn dev
```

The app will be available at `http://localhost:3000`. The camera will work on localhost.

### Building for Production

```bash
# Build the application
npm run build
# or
yarn build

# Preview production build
npm run preview
# or
yarn preview
```

### Testing

```bash
# Run tests
npm test
# or
yarn test

# Run tests with UI
npm run test:ui
# or
yarn test:ui
```

### Linting & Formatting

```bash
# Lint code
npm run lint
# or
yarn lint

# Fix linting issues
npm run lint:fix
# or
yarn lint:fix

# Format code
npm run format
# or
yarn format
```

## 📷 Camera Requirements

### HTTPS Requirement

Modern browsers require **HTTPS** for camera access (except on localhost). To use the camera feature in production:

1. **Deploy to HTTPS-enabled hosting** (Vercel, Netlify, etc.)
2. **Use a reverse proxy** with SSL certificate
3. **Test locally** on `localhost` (works without HTTPS)

### Camera Permissions

The first time you access the scan page, your browser will request camera permissions. Make sure to:

- Allow camera access when prompted
- Check browser settings if permission is denied
- Use the manual barcode input as a fallback

### Mobile Testing

To test on mobile devices over your local network:

1. Find your computer's local IP address
2. Access `http://[YOUR_IP]:3000` from your mobile device
3. Note: Camera may not work over HTTP on mobile (use HTTPS in production)

## 🎯 Usage Guide

### Scanning Products

1. Navigate to the **Scan** page (default route)
2. Allow camera permissions when prompted
3. Point your camera at a product barcode
4. The product will be automatically added to your cart
5. Use manual input if camera is unavailable

### Browsing Catalog

1. Navigate to the **Catalog** page
2. Search products by name, SKU, or barcode
3. Click "Add to Cart" on any product
4. View cart badge in the top navigation

### Managing Cart

1. Navigate to the **Cart** page
2. Adjust quantities using +/- buttons
3. Remove items with the × button
4. Click "Proceed to Checkout" when ready

### Checkout

1. Fill in customer information (name and email required)
2. Review your order summary
3. Click "Pay Now" to simulate payment
4. Order is created and stored locally
5. Redirected to success page with order details

### Viewing Orders

1. Navigate to the **Orders** page
2. View all past orders
3. Click any order to see full details

## 🗂 Data Management

### Products

Products are loaded from `src/data/products.json`. To add or modify products:

```json
{
  "id": "p1",
  "barcode": "7290001234567",
  "name": "Water 1.5L",
  "priceInCents": 390,
  "sku": "WAT-15",
  "imageUrl": "optional-image-url"
}
```

### State Persistence

- **Cart**: Persisted to `localStorage` automatically
- **Orders**: Persisted to `localStorage` automatically
- **Catalog**: Loaded from JSON on app start

To clear all data: Open browser DevTools → Application → Local Storage → Delete `scan-and-pay-storage`

## 🎨 Theming & Styling

The app uses a centralized theme in `src/styles/theme.ts`. Customize:

- Colors (primary, secondary, backgrounds)
- Typography (fonts, sizes, weights)
- Spacing (consistent spacing scale)
- Border radius, shadows, transitions
- Responsive breakpoints

All components use styled-components with theme access:

```typescript
import styled from 'styled-components';
import { theme } from '@/styles/theme';

const Button = styled.button`
  background-color: ${theme.colors.primary};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
`;
```

## 🧪 Testing Strategy

### Unit Tests

- Store slices (cart, catalog, orders)
- Utility functions (currency formatting)
- Component logic

### Component Tests

- UI rendering
- User interactions
- Accessibility features

Run tests in watch mode during development:

```bash
npm test
```

## ♿ Accessibility Features

- Semantic HTML elements
- ARIA labels and live regions
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast ratios
- Respect `prefers-reduced-motion`

## 📱 Progressive Web App (PWA)

The app includes a basic PWA setup in `src/lib/pwa/registerSW.ts`. To enhance:

1. Add a service worker with Workbox
2. Create a web manifest (`manifest.json`)
3. Add offline functionality
4. Enable install prompt

## 🔒 Security Notes

- No real payment processing (simulation only)
- No authentication/authorization (demo app)
- All data stored client-side (localStorage)
- No backend API calls

**For production use**, implement:
- Secure payment gateway integration
- User authentication
- Server-side order processing
- Input validation and sanitization

## 🚀 Deployment

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
```

### Build Configuration

- Build command: `npm run build`
- Output directory: `dist`
- Node version: 18+

## 🐛 Troubleshooting

### Camera Not Working

- **Issue**: Permission denied or camera not found
- **Solution**: 
  - Check browser permissions
  - Ensure HTTPS or localhost
  - Use manual barcode input as fallback

### Build Errors

- **Issue**: TypeScript errors during build
- **Solution**: 
  - Run `npm run type-check`
  - Fix any type errors
  - Ensure all dependencies are installed

### Tests Failing

- **Issue**: Tests not passing
- **Solution**:
  - Run `npm test` to see detailed errors
  - Check test setup in `src/test/setup.ts`
  - Ensure jsdom environment is configured

### Styling Issues

- **Issue**: Components not styled correctly
- **Solution**:
  - Verify styled-components is installed
  - Check theme imports
  - Clear browser cache

## 📝 License

This project is provided as-is for demonstration purposes.

## 🤝 Contributing

This is a demo project. For improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📧 Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ using React + TypeScript + Vite**

