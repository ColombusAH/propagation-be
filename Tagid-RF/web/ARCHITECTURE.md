# Architecture Overview

## Design Principles

This application follows modern React best practices with a focus on:

1. **Separation of Concerns**: Clear boundaries between UI, state, and business logic
2. **Type Safety**: Full TypeScript coverage with strict mode enabled
3. **Component Composition**: Reusable, single-responsibility components
4. **Immutable State**: Zustand with immer for predictable state updates
5. **Mobile-First**: Responsive design prioritizing mobile experience

## Architecture Layers

### 1. Presentation Layer (`src/components`, `src/pages`)

**Components**: Reusable UI building blocks
- `Layout.tsx`: Page wrapper with navigation
- `TopBar.tsx`: Main navigation with cart badge
- `CameraView.tsx`: Barcode scanner interface
- `ProductCard.tsx`: Product display card
- `QuantityInput.tsx`: Cart quantity control
- `EmptyState.tsx`: Empty state messaging

**Pages**: Route-specific views
- `ScanPage.tsx`: Camera scanner + manual input
- `CatalogPage.tsx`: Product grid with search
- `CartPage.tsx`: Shopping cart management
- `CheckoutPage.tsx`: Order form + payment
- `OrderSuccessPage.tsx`: Post-order confirmation
- `OrdersPage.tsx`: Order history list

### 2. State Management Layer (`src/store`)

**Zustand Store Architecture**

```
Store (Combined)
├── CatalogSlice
│   ├── products[]
│   ├── loadProducts()
│   ├── getProductById()
│   ├── getProductByBarcode()
│   └── searchProducts()
├── CartSlice
│   ├── items[]
│   ├── addByProductId()
│   ├── addByBarcode()
│   ├── setQty()
│   ├── remove()
│   ├── clear()
│   ├── getTotalInCents()
│   └── getCartItemCount()
└── OrdersSlice
    ├── orders[]
    ├── createOrder()
    ├── getById()
    └── list()
```

**Persistence Strategy**
- Cart and Orders: Persisted to localStorage
- Catalog: Loaded from JSON on startup
- Hydration: Automatic on app mount

### 3. Business Logic Layer (`src/lib`, `src/payment`)

**Barcode Scanner** (`lib/barcode/BarcodeScanner.ts`)
- Wraps @zxing/browser for cleaner API
- Handles camera enumeration and selection
- Implements scan throttling (800ms default)
- Provides lifecycle management (start/stop)

**Payment Provider** (`payment/SimplePaymentProvider.ts`)
- Simulates payment processing (600ms latency)
- Generates order IDs (UUID v4)
- Creates order records in store
- Returns payment result

**Utilities** (`lib/utils/`)
- `currency.ts`: Money formatting (cents → locale currency)
- `uuid.ts`: Simple UUID v4 generation

### 4. Data Layer (`src/data`)

**Products** (`products.json`)
```typescript
interface Product {
  id: string;          // Unique identifier
  barcode: string;     // Scannable code
  name: string;        // Display name
  priceInCents: number;// Price (cents for precision)
  sku?: string;        // Stock keeping unit
  imageUrl?: string;   // Product image
}
```

### 5. Styling Layer (`src/styles`)

**Theme System**
- Centralized design tokens (colors, spacing, typography)
- Consistent breakpoints for responsive design
- Reusable shadow and transition definitions
- Type-safe theme access via styled-components

**Global Styles**
- CSS reset and normalization
- Base typography and layout
- Accessibility considerations (prefers-reduced-motion)

## Data Flow

### Scanning Flow

```
User points camera at barcode
    ↓
BarcodeScanner.onScan(barcode)
    ↓
ScanPage.handleScan(barcode)
    ↓
cartSlice.addByBarcode(barcode)
    ↓
catalogSlice.getProductByBarcode(barcode)
    ↓
cartSlice.addByProductId(productId)
    ↓
State updated & persisted
    ↓
UI re-renders with new cart count
```

### Checkout Flow

```
User clicks "Proceed to Checkout"
    ↓
Navigate to /checkout
    ↓
User fills form (name, email, note)
    ↓
Form validation
    ↓
paySimple() called
    ↓
Simulate network delay (600ms)
    ↓
Generate orderId (UUID)
    ↓
ordersSlice.createOrder(order)
    ↓
cartSlice.clear()
    ↓
Navigate to /orders/:orderId/success
```

## State Management Rationale

**Why Zustand?**
- Lightweight (~1KB) compared to Redux
- Minimal boilerplate
- Built-in persistence middleware
- TypeScript-first design
- No context provider needed

**Slice Pattern**
- Logical separation of concerns
- Easy to test individual slices
- Composable state management
- Clear ownership of state domains

## Component Architecture

**Container/Presenter Pattern** (Light)
- Pages: Smart components (state + effects)
- Components: Presentational (props in, UI out)
- Hooks: Shared logic extraction

**Styling Strategy**
- Styled-components for CSS-in-JS
- Co-located styles with components
- Theme-driven design system
- No CSS modules or separate stylesheets

## Testing Strategy

**Unit Tests**
- Store slices (business logic)
- Utility functions (pure functions)
- Complex component logic

**Integration Tests**
- User flows (scan → add → checkout)
- State persistence
- Route transitions

**Not Included (but recommended for production)**
- E2E tests (Playwright/Cypress)
- Visual regression tests (Chromatic)
- Performance tests (Lighthouse CI)

## Performance Considerations

**Bundle Optimization**
- Vite's automatic code splitting
- Tree-shaking of unused exports
- Dynamic imports for heavy features (future)

**Runtime Performance**
- Zustand: Efficient shallow equality checks
- React 18: Concurrent rendering
- CSS-in-JS: Minimal runtime overhead with styled-components

**Mobile Optimization**
- Responsive images (future)
- Touch-friendly UI (44px+ tap targets)
- Throttled camera scanning (reduces CPU)

## Security Considerations

**Current State (MVP)**
- Client-side only (no backend)
- No authentication required
- No real payment processing
- LocalStorage for data (not secure)

**Production Requirements**
- HTTPS everywhere (required for camera)
- Input sanitization and validation
- CSP headers
- Secure payment gateway (Stripe/PayPal)
- Backend API with authentication
- Encrypted data storage
- Rate limiting and CORS

## Scalability Path

**Phase 1: Current MVP**
- Local products.json
- Client-side state
- No backend

**Phase 2: Backend Integration**
- REST/GraphQL API
- Product database (PostgreSQL)
- User authentication (JWT)
- Real payment gateway

**Phase 3: Advanced Features**
- Real-time inventory sync
- Push notifications (PWA)
- Offline mode with sync
- Analytics and reporting
- Multi-language support
- Admin dashboard

## Browser Support

**Minimum Requirements**
- Chrome 90+
- Safari 14+
- Firefox 88+
- Edge 90+

**Camera API Requirements**
- getUserMedia() support
- HTTPS or localhost

**Fallback Strategy**
- Manual barcode entry
- Feature detection
- Graceful degradation

## Development Workflow

1. **Local Development**: `npm run dev`
2. **Type Checking**: `npm run type-check`
3. **Linting**: `npm run lint`
4. **Testing**: `npm test`
5. **Building**: `npm run build`
6. **Preview**: `npm run preview`

## Deployment Checklist

- [ ] Build passes without errors
- [ ] All tests pass
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] Environment variables set
- [ ] HTTPS configured
- [ ] Camera permissions tested
- [ ] Mobile responsive tested
- [ ] Accessibility audit passed
- [ ] Performance metrics acceptable

## Future Enhancements

### High Priority
- Real payment gateway integration
- Backend API for products and orders
- User authentication and profiles
- Product image support
- Better camera controls (zoom, focus)

### Medium Priority
- PWA with offline support
- Push notifications for order updates
- Barcode history and favorites
- Multiple payment methods
- Receipt generation (PDF)

### Low Priority
- Multi-language support
- Dark mode theme
- Advanced search and filters
- Product recommendations
- Loyalty program integration

---

**Last Updated**: November 2025

