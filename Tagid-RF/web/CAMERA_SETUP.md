# Camera Setup & Troubleshooting Guide

## Overview

The Scan & Pay app uses the device camera to scan barcodes in real-time. This guide explains how to set up and troubleshoot camera access.

## Requirements

### Browser Requirements
- **Chrome/Edge**: 90+
- **Safari**: 14+
- **Firefox**: 88+
- **Mobile Browsers**: iOS Safari 14+, Chrome Mobile 90+

### Security Requirements
Camera access requires one of the following:
- **HTTPS** (secure connection) - Required for production
- **localhost** - Works for local development
- **127.0.0.1** - Works for local development

⚠️ **Important**: Camera will NOT work over HTTP (except localhost)

## Development Setup

### Local Development (Recommended)

```bash
npm run dev
```

The app runs on `http://localhost:3000` by default, which allows camera access.

### Testing on Mobile Devices

To test on a mobile device over your local network, you need HTTPS:

#### Option 1: Using Vite with HTTPS (Recommended)

1. Generate SSL certificates:
```bash
# Install mkcert (one-time setup)
brew install mkcert  # macOS
# or
choco install mkcert  # Windows

# Create local CA
mkcert -install

# Generate certificates for your project
cd scan-and-pay-web
mkcert localhost 127.0.0.1 192.168.1.x  # Replace with your local IP
```

2. Update `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    https: {
      key: './localhost+2-key.pem',
      cert: './localhost+2.pem',
    },
    host: true,
    port: 3000,
  },
});
```

3. Start the server:
```bash
npm run dev
```

4. Access from mobile:
```
https://192.168.1.x:3000  # Replace with your local IP
```

#### Option 2: Using ngrok (Easier, but slower)

```bash
# Install ngrok
npm install -g ngrok

# Start your dev server
npm run dev

# In another terminal, create HTTPS tunnel
ngrok http 3000

# Access via the ngrok HTTPS URL from any device
```

## Camera Permissions

### First-Time Setup

1. Navigate to `/scan` page
2. Browser will prompt: "Allow camera access?"
3. Click **Allow**
4. Camera should start automatically

### Permission Denied

If you accidentally denied camera permissions:

#### Chrome/Edge (Desktop)
1. Click the 🔒 (lock icon) in address bar
2. Find "Camera" → Select "Allow"
3. Refresh the page

#### Chrome (Mobile)
1. Open browser settings
2. Go to Site Settings → Camera
3. Find your site → Select "Allow"
4. Refresh the page

#### Safari (iOS)
1. Go to iOS Settings → Safari → Camera
2. Select "Ask" or "Allow"
3. Refresh the page

#### Firefox
1. Click the 🔒 (lock icon) in address bar
2. Click "More Information" → Permissions
3. Camera → Uncheck "Use Default" → Select "Allow"
4. Refresh the page

## Camera Features

### Automatic Camera Selection

The app automatically selects the best camera:
1. **Mobile**: Tries to use rear/back camera first
2. **Desktop**: Uses default webcam
3. Falls back to first available camera if preferred not found

### Multiple Cameras

If your device has multiple cameras, you'll see a "🔄 Switch Camera" button to cycle through them.

### Manual Fallback

If camera doesn't work, you can always use the **Manual Entry** section to type barcodes.

## Troubleshooting

### Camera Not Starting

#### Issue: "Camera access requires HTTPS or localhost"
**Solution**: 
- Use `http://localhost:3000` for local testing
- Use HTTPS for remote access (see setup above)
- Deploy to Vercel/Netlify (automatic HTTPS)

#### Issue: "Camera permission denied"
**Solution**: 
- Check browser permissions (see above)
- Clear site data and try again
- Check if camera is being used by another app

#### Issue: "No cameras found on this device"
**Solution**: 
- Ensure your device has a camera
- Check if camera drivers are installed (desktop)
- Try a different browser
- Restart your device

#### Issue: "Camera is already in use"
**Solution**: 
- Close other apps using the camera (Zoom, Skype, etc.)
- Close other browser tabs accessing the camera
- Restart the browser

### Camera Shows Black Screen

**Possible Causes**:
1. Camera is covered or obstructed
2. Camera is being used by another app
3. Browser doesn't have camera permissions
4. Camera driver issue (desktop)

**Solutions**:
- Check physical camera (is it covered?)
- Close other camera apps
- Restart browser
- Update camera drivers (desktop)
- Try a different browser

### Scanning Not Working

#### Issue: Barcode not detected
**Solution**:
- Ensure good lighting
- Hold barcode 6-12 inches from camera
- Keep barcode flat and steady
- Try adjusting angle
- Ensure barcode is not damaged or dirty

#### Issue: Wrong product detected
**Solution**:
- Hold camera steady for 1 second
- Ensure only one barcode is visible
- Check if correct barcode is being scanned

### Performance Issues

#### Issue: Camera is laggy or slow
**Solution**:
- Close other browser tabs
- Restart browser
- Clear browser cache
- Use a more powerful device
- Reduce browser extensions

## Testing Camera Functionality

### Test Checklist

- [ ] Camera permission prompt appears
- [ ] Camera starts and shows video feed
- [ ] Scan targeting box is visible
- [ ] Can scan a barcode successfully
- [ ] Vibration feedback works (mobile)
- [ ] Toast notification appears after scan
- [ ] Product is added to cart
- [ ] Switch camera button appears (if multiple cameras)
- [ ] Manual input fallback works
- [ ] Error messages are clear and helpful

### Test Barcodes

The app includes these test products with barcodes:

```
7290001234567 - Water 1.5L
7290007654321 - Bread Whole Wheat
7290005551234 - Orange Juice 1L
7290009998888 - Greek Yogurt
7290002223333 - Bananas (1kg)
7290008887777 - Chicken Breast (500g)
7290003334444 - Tomatoes (1kg)
7290006665555 - Mozzarella Cheese
7290004445555 - Coffee Beans (250g)
7290001119999 - Chocolate Bar
```

You can:
1. Print these barcodes for testing
2. Display them on another screen
3. Use online barcode generator to create test codes
4. Use manual input to test without camera

## Browser Console Debugging

Open browser console (F12) to see detailed error messages:

```javascript
// Check camera support
console.log('Camera supported:', !!navigator.mediaDevices);
console.log('Secure context:', window.isSecureContext);
console.log('Hostname:', window.location.hostname);

// List cameras manually
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    const cameras = devices.filter(d => d.kind === 'videoinput');
    console.log('Available cameras:', cameras);
  });

// Test camera access
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    console.log('Camera access granted!');
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(error => {
    console.error('Camera access error:', error.name, error.message);
  });
```

## Production Deployment

### Recommended Platforms (Auto HTTPS)

1. **Vercel** (Easiest)
```bash
npm install -g vercel
vercel
```

2. **Netlify**
```bash
npm install -g netlify-cli
netlify deploy --prod
```

3. **GitHub Pages** (Requires custom domain for HTTPS)
4. **AWS Amplify**
5. **Firebase Hosting**

All these platforms provide automatic HTTPS, which enables camera access.

### Custom Server

If deploying to your own server:
1. Obtain SSL certificate (Let's Encrypt is free)
2. Configure HTTPS on your web server
3. Redirect HTTP to HTTPS
4. Test camera access after deployment

## Mobile-Specific Tips

### iOS (iPhone/iPad)

- ✅ Works in Safari (iOS 14.3+)
- ✅ Works in Chrome for iOS
- ⚠️ In-app browsers (Facebook, Instagram) may have issues
- 💡 Best experience: Add to Home Screen

### Android

- ✅ Works in Chrome (recommended)
- ✅ Works in Firefox
- ✅ Works in Samsung Internet
- ⚠️ Some older devices may be slow
- 💡 Ensure good lighting for better performance

### Tips for Better Scanning

1. **Lighting**: Natural or bright artificial light works best
2. **Distance**: Hold phone 6-12 inches from barcode
3. **Angle**: Keep barcode flat and parallel to camera
4. **Stability**: Hold phone steady for 1 second
5. **Focus**: Tap screen to focus (if camera supports it)

## Common Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Camera access requires HTTPS" | Using HTTP (not localhost) | Use localhost or HTTPS |
| "Camera permission denied" | User denied permission | Update browser permissions |
| "No cameras found" | No camera hardware | Use manual input |
| "Camera is already in use" | Another app using camera | Close other camera apps |
| "Camera not supported" | Old browser | Update browser |
| "NotAllowedError" | Permission denied | Check browser settings |
| "NotFoundError" | No camera hardware | Use manual input |
| "NotReadableError" | Camera in use elsewhere | Close other apps |
| "SecurityError" | Not HTTPS/localhost | Use secure connection |

## Support

If you continue to experience issues:

1. Check browser console for detailed errors
2. Try a different browser
3. Try a different device
4. Use manual input as fallback
5. Report issue with:
   - Browser name and version
   - Device type
   - Error message from console
   - Steps to reproduce

## Additional Resources

- [MDN: getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [Can I Use: getUserMedia](https://caniuse.com/stream)
- [WebRTC Samples](https://webrtc.github.io/samples/)
- [ZXing Documentation](https://github.com/zxing-js/library)

---

**Last Updated**: November 2025
**Camera Library**: @zxing/browser v0.1.5
**Supported Barcode Types**: All major formats (EAN, UPC, QR, Code128, etc.)

