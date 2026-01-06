# Quick Start Guide

## 🚀 Get Up and Running in 3 Minutes

### 1. Install Dependencies

```bash
cd scan-and-pay-web
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### 3. Test the Features

#### Scan a Barcode
1. Navigate to the **Scan** page (opens by default)
2. Allow camera permissions
3. Scan one of these test barcodes:
   - `0001` - Banana
   - `7290001234567` - Water
   - `8412345678901` - Pasta
4. Or enter manually in the fallback input

#### Browse Catalog
1. Click **Catalog** in the nav bar
2. Search for "milk" or "bread"
3. Click "Add to Cart" on any product

#### Complete a Purchase
1. Add items to cart
2. Click **Cart** (see the badge count)
3. Adjust quantities or remove items
4. Click "Proceed to Checkout"
5. Fill in:
   - Name: `John Doe`
   - Email: `john@example.com`
6. Click "Pay Now"
7. View your order confirmation!

#### View Orders
1. Click **Orders** in the nav bar
2. See all completed orders
3. Click any order for details

## 📱 Test on Mobile

### Option 1: Localhost (Camera works)
```bash
# Find your IP address
ipconfig getifaddr en0  # macOS
ip addr show           # Linux

# Access from mobile
http://[YOUR_IP]:3000
```

### Option 2: Deploy to HTTPS
```bash
# Deploy to Vercel (free)
npm i -g vercel
vercel
```

## 🧪 Run Tests

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# With UI
npm run test:ui
```

## 🔨 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm test` | Run tests |
| `npm run lint` | Check for linting errors |
| `npm run lint:fix` | Fix linting errors |
| `npm run format` | Format code with Prettier |
| `npm run type-check` | Check TypeScript types |

## 🎯 Key Files to Know

- **Add Products**: `src/data/products.json`
- **Theme/Colors**: `src/styles/theme.ts`
- **Store Logic**: `src/store/slices/`
- **Pages**: `src/pages/`
- **Components**: `src/components/`

## 🐛 Common Issues

### Camera Not Working?
- ✅ Check you're on localhost or HTTPS
- ✅ Allow camera permissions in browser
- ✅ Use manual input as fallback

### Build Failing?
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors?
```bash
npm run type-check
```

## 📚 Learn More

- Full documentation: [README.md](./README.md)
- Architecture details: [ARCHITECTURE.md](./ARCHITECTURE.md)
- React + TypeScript: [React Docs](https://react.dev)
- Zustand state: [Zustand Docs](https://docs.pmnd.rs/zustand)

## 🎨 Customize

### Change Primary Color
Edit `src/styles/theme.ts`:
```typescript
colors: {
  primary: '#2563eb', // Change this!
  // ...
}
```

### Add New Product
Edit `src/data/products.json`:
```json
{
  "id": "p11",
  "barcode": "1234567890123",
  "name": "Your Product",
  "priceInCents": 999,
  "sku": "YOUR-SKU"
}
```

### Modify Layout
Edit `src/components/Layout.tsx` or `src/components/TopBar.tsx`

## ✅ Verification Checklist

After setup, verify:

- [ ] `npm run dev` starts successfully
- [ ] App opens at localhost:3000
- [ ] Camera scanner appears on /scan
- [ ] Can add products from catalog
- [ ] Cart persists on page refresh
- [ ] Can complete checkout flow
- [ ] Orders appear in history
- [ ] Tests pass with `npm test`

## 🚢 Deploy to Production

### Vercel (Recommended)
```bash
npm i -g vercel
vercel
```

### Netlify
```bash
npm i -g netlify-cli
netlify deploy --prod
```

### Manual
```bash
npm run build
# Upload 'dist' folder to your host
```

---

**Need help?** Check [README.md](./README.md) for detailed documentation.

