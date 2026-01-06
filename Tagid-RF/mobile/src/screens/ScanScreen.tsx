// src/screens/ScanScreen.tsx
import { useCart } from '@/src/store/cart'
import { BarcodeScanningResult, CameraView, useCameraPermissions } from 'expo-camera'
import { router, useFocusEffect } from 'expo-router'
import { useCallback, useEffect, useState } from 'react'
import { Button, StyleSheet, Text, View } from 'react-native'

export default function ScanScreen() {
  const [perm, requestPerm] = useCameraPermissions()
  const add = useCart(s => s.add)
  const [scanned, setScanned] = useState(false)
  const [isActive, setIsActive] = useState(false)

  useEffect(() => { if (!perm?.granted) requestPerm() }, [perm])

  // Only activate camera when screen is focused
  useFocusEffect(
    useCallback(() => {
      console.log('📷 Scan screen focused - Camera active')
      setIsActive(true)
      return () => {
        console.log('👋 Scan screen unfocused - Camera inactive')
        setIsActive(false)
        setScanned(false) // Reset scanned state when leaving
      }
    }, [])
  )

  const onBarcodeScanned = ({ data, type }: BarcodeScanningResult) => {
    if (scanned) return
    setScanned(true)

    console.log('📷 Scanned:', { data, type })

    // Parse QR or barcode payload -> product lookup
    const product = resolveProductByCode(data)
    
    if (product) {
      console.log('✅ Product found:', product)
      add(product)
      router.push('/(tabs)/two')
    } else {
      console.log('❌ Product not found for code:', data)
      alert(`Product not found: ${data}`)
    }
    
    setTimeout(() => setScanned(false), 1000)
  }

  if (!perm?.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>📷</Text>
        <Text style={styles.permissionTitle}>Camera Permission Required</Text>
        <Text style={styles.permissionSubtitle}>
          We need camera access to scan barcodes
        </Text>
        <View style={styles.permissionButton}>
          <Button title="Grant Permission" onPress={requestPerm} />
        </View>
      </View>
    )
  }

  // Only render camera when screen is active (focused)
  if (!isActive) {
    return (
      <View style={styles.inactiveContainer}>
        <Text style={styles.inactiveText}>Camera paused</Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={styles.camera}
        onBarcodeScanned={onBarcodeScanned}
        barcodeScannerSettings={{ barcodeTypes: ['qr', 'ean13', 'ean8', 'upc_a', 'upc_e'] }}
      />
      
      {/* Scanning Guide Overlay - Using absolute positioning */}
      <View style={styles.overlay}>
        <View style={styles.scanArea}>
          <View style={[styles.corner, styles.topLeft]} />
          <View style={[styles.corner, styles.topRight]} />
          <View style={[styles.corner, styles.bottomLeft]} />
          <View style={[styles.corner, styles.bottomRight]} />
        </View>
        <Text style={styles.instructionText}>
          Place barcode within the green square
        </Text>
      </View>
      
      <View style={styles.footer}>
        <Button title="Go to Cart" onPress={() => router.push('/(tabs)/two')} />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 80, // Leave space for footer
    justifyContent: 'center',
    alignItems: 'center',
    pointerEvents: 'none', // Allow camera to receive touch events
  },
  scanArea: {
    width: 250,
    height: 250,
    position: 'relative',
  },
  corner: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderColor: '#00FF00',
    borderWidth: 4,
  },
  topLeft: {
    top: 0,
    left: 0,
    borderRightWidth: 0,
    borderBottomWidth: 0,
  },
  topRight: {
    top: 0,
    right: 0,
    borderLeftWidth: 0,
    borderBottomWidth: 0,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderRightWidth: 0,
    borderTopWidth: 0,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderLeftWidth: 0,
    borderTopWidth: 0,
  },
  instructionText: {
    marginTop: 20,
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    padding: 10,
    borderRadius: 8,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 15,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F5F5F5',
  },
  permissionText: {
    fontSize: 80,
    marginBottom: 20,
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
    textAlign: 'center',
  },
  permissionSubtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    textAlign: 'center',
  },
  permissionButton: {
    width: 200,
  },
  inactiveContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000000',
  },
  inactiveText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
  },
});

function resolveProductByCode(code: string) {
  // Quick hardcoded map for MVP. Replace with backend call.
  const catalog: Record<string, {id:string;title:string;priceInCents:number}> = {
    "7290001234567": { id:"prod_TIlNsCc5BSJvxa", title:"Jeans 501", priceInCents: 20000 },
    "0001": { id:"prod_TIlNbDb8k04BMA", title:"Jeans 502", priceInCents: 1800 },
  }
  console.log(catalog)
  return catalog[code] ?? null
}
