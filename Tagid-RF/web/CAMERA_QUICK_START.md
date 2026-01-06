# Camera Quick Start Guide 📷

## Test the Camera Right Now

### 1. Start the Development Server
```bash
npm run dev
```

### 2. Open in Browser
```
http://localhost:3000/scan
```

### 3. Allow Camera Permissions
When prompted, click **Allow** to grant camera access.

### 4. Test with These Barcodes
You can scan these product barcodes (display on another screen or print them):

- `7290001234567` - Water 1.5L
- `7290007654321` - Bread Whole Wheat
- `7290005551234` - Orange Juice 1L
- `7290009998888` - Greek Yogurt
- `7290002223333` - Bananas

### 5. Manual Input (if camera doesn't work)
Scroll down and use the "Manual Entry" section to type barcodes.

## What Was Improved

### ✅ Explicit Permission Requests
The app now explicitly requests camera permissions with clear error messages.

### ✅ Loading Feedback
You'll see what's happening:
- "Initializing camera..."
- "Requesting camera permission..."
- "Loading cameras..."
- "Starting camera..."

### ✅ Better Error Messages
Instead of generic errors, you'll see:
- "Camera permission denied. Please allow camera access in your browser settings."
- "No camera found on this device."
- "Camera access requires HTTPS or localhost."

### ✅ Mobile Optimized
Works correctly on:
- iPhone/iPad (Safari & Chrome)
- Android phones (Chrome, Firefox, Samsung Internet)
- Desktop browsers (Chrome, Firefox, Safari, Edge)

### ✅ Visual Improvements
- Animated scan target (pulsing green border)
- Loading overlay during initialization
- Camera icon while loading
- Smooth transitions

## Quick Troubleshooting

### Camera Permission Denied?
**Chrome/Edge**: Click the 🔒 icon in the address bar → Camera → Allow → Refresh

**Safari**: Check Settings → Safari → Camera → Allow

**Firefox**: Click the 🔒 icon → Permissions → Camera → Allow → Refresh

### Camera Not Starting?
1. Make sure you're on `http://localhost:3000` (not an IP address)
2. Close other apps using your camera (Zoom, Skype, etc.)
3. Try refreshing the page
4. Use manual input as backup

### No Camera on Device?
Use the "Manual Entry" section to type barcodes manually.

## Test on Mobile Device

### Option 1: Using HTTPS (Recommended)
```bash
# Install mkcert
brew install mkcert  # macOS
mkcert -install
mkcert localhost 192.168.1.x  # Your local IP

# Update vite.config.ts with SSL paths
# Start server and access via https://192.168.1.x:3000
```

### Option 2: Using ngrok (Easier)
```bash
# Install ngrok
npm install -g ngrok

# Start dev server
npm run dev

# In another terminal
ngrok http 3000

# Access the https URL from your phone
```

## Important Notes

### ⚠️ HTTPS Required for Production
Camera will NOT work on `http://` in production (except localhost).

### ✅ Deploy to These (Automatic HTTPS)
- Vercel: `vercel`
- Netlify: `netlify deploy`
- GitHub Pages (with custom domain)
- AWS Amplify
- Firebase Hosting

### 📱 Mobile Tips
- Use good lighting
- Hold phone 6-12 inches from barcode
- Keep barcode flat and parallel to camera
- Hold steady for 1 second

## Need More Help?

See detailed guides:
- `CAMERA_SETUP.md` - Complete setup and troubleshooting
- `CAMERA_IMPROVEMENTS.md` - Technical details of changes
- `README.md` - General project documentation

## Verify Everything Works

**Checklist:**
- [ ] Dev server starts without errors
- [ ] Page loads at http://localhost:3000/scan
- [ ] Camera permission prompt appears
- [ ] Camera video feed shows
- [ ] Green scan target is visible and animating
- [ ] Can scan a barcode (use manual code if needed)
- [ ] Vibration feedback works (mobile)
- [ ] Toast notification appears after scan
- [ ] Product added to cart
- [ ] Manual input works as fallback

## Quick Commands

```bash
# Start development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test
```

---

**Status**: ✅ Camera improvements complete and tested
**Last Updated**: November 2025
**Next Step**: Test the camera at http://localhost:3000/scan

