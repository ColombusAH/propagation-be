# Installation & Setup

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: Version 18 or higher
- **npm** or **yarn**: Package manager
- **Modern browser**: Chrome 90+, Safari 14+, Firefox 88+, or Edge 90+

## Step-by-Step Installation

### 1. Navigate to Project Directory

```bash
cd /Users/anverh/scan-and-pay-web
```

### 2. Install Dependencies

Using npm:
```bash
npm install
```

Using yarn:
```bash
yarn install
```

This will install all required dependencies including:
- React 18 and React DOM
- TypeScript
- Vite (build tool)
- Zustand (state management)
- React Router (routing)
- styled-components (styling)
- @zxing/browser (barcode scanning)
- Vitest (testing)
- ESLint and Prettier (code quality)

**Installation time:** Approximately 1-2 minutes depending on your internet connection.

### 3. Verify Installation

Check that everything installed correctly:

```bash
npm run type-check
```

This should complete without errors.

### 4. Start Development Server

```bash
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 5. Open in Browser

Navigate to: `http://localhost:3000`

You should see the Scan & Pay application with the camera scanner on the main page.

## First-Time Setup

### Allow Camera Permissions

When you first visit the scan page:

1. Browser will request camera permission
2. Click **Allow** or **Grant**
3. If denied, use the manual barcode entry fallback
4. To reset permissions: Browser Settings → Site Settings → Camera

### Test Basic Functionality

1. **Test Manual Entry**
   - Enter barcode: `0001`
   - Click "Add"
   - Should see toast: "Added Banana to cart"

2. **Check Cart**
   - Click "Cart" in navigation
   - See cart badge shows "1"
   - View cart contents

3. **Browse Catalog**
   - Click "Catalog" in navigation
   - Search for "water"
   - Add items to cart

4. **Complete Checkout**
   - Navigate to Cart
   - Click "Proceed to Checkout"
   - Fill form:
     - Name: Test User
     - Email: test@example.com
   - Click "Pay Now"
   - View order confirmation

## Development Workflow

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui
```

### Code Quality

```bash
# Check for linting errors
npm run lint

# Auto-fix linting errors
npm run lint:fix

# Format code
npm run format

# Check TypeScript types
npm run type-check
```

### Building for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

The production build will be in the `dist/` directory.

## Troubleshooting

### Issue: "Cannot find module" errors

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 3000 already in use

**Solution:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in vite.config.ts:
server: {
  port: 3001,
}
```

### Issue: Camera not working

**Solutions:**
1. Ensure you're on localhost or HTTPS
2. Check browser camera permissions
3. Try different browser (Chrome recommended)
4. Use manual barcode entry fallback

### Issue: TypeScript errors

**Solution:**
```bash
# Check what's wrong
npm run type-check

# If persists, restart TypeScript server
# In VSCode: Cmd+Shift+P → "TypeScript: Restart TS Server"
```

### Issue: Tests failing

**Solution:**
```bash
# Run tests with verbose output
npm test -- --reporter=verbose

# Check test setup
cat src/test/setup.ts
```

## Environment Configuration

### Optional: Create .env.local

```bash
cp .env.example .env.local
```

Edit `.env.local` to customize:
```env
PORT=3000
```

### Node Version

The project uses Node 18. If you have nvm:

```bash
# Use correct Node version
nvm use

# Or install Node 18
nvm install 18
nvm use 18
```

## IDE Setup

### VS Code (Recommended)

Install recommended extensions:
- ESLint
- Prettier
- TypeScript
- Styled Components

### Settings

Add to `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Next Steps

After successful installation:

1. ✅ Read [QUICKSTART.md](./QUICKSTART.md) for feature tour
2. ✅ Review [README.md](./README.md) for full documentation
3. ✅ Check [ARCHITECTURE.md](./ARCHITECTURE.md) for code structure
4. ✅ Explore [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) for overview

## Getting Help

If you encounter issues:

1. Check [README.md](./README.md) → Troubleshooting section
2. Verify Node.js version: `node --version` (should be 18+)
3. Check console for error messages
4. Try clean install (delete node_modules)

## Verification Checklist

After installation, verify:

- [ ] `npm install` completed without errors
- [ ] `npm run dev` starts successfully
- [ ] Browser opens to localhost:3000
- [ ] App loads without errors
- [ ] Can navigate between pages
- [ ] Can add product manually (barcode: 0001)
- [ ] Cart persists on page refresh
- [ ] `npm test` runs successfully
- [ ] `npm run build` completes without errors

## Installation Complete! 🎉

Your Scan & Pay application is now ready to use.

Start the development server with:
```bash
npm run dev
```

Then open `http://localhost:3000` in your browser.

Happy coding! 🚀

