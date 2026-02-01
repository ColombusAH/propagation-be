// src/screens/PayScreen.tsx
import PaymentStatus from '@/src/components/PaymentStatus'
import { PAYMENT_CONFIG, getAPIUrl, getReturnUrl } from '@/src/config/payment'
import { useCart } from '@/src/store/cart'
import { useStripe } from '@stripe/stripe-react-native'
import { router } from 'expo-router'
import { useEffect, useState } from 'react'
import { ActivityIndicator, Alert, Button, ScrollView, Text, View } from 'react-native'

export default function PayScreen() {
  const { initPaymentSheet, presentPaymentSheet } = useStripe()
  const { items, clear } = useCart()
  const [ready, setReady] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [paymentData, setPaymentData] = useState<any>(null)

  const total = items.reduce((sum, item) => sum + item.priceInCents * item.qty, 0)

  useEffect(() => {
    initializePayment()
  }, [])

  const initializePayment = async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('💳 Initializing payment...')
      console.log('Items in cart:', items)
      console.log('Total amount:', total, 'cents')

      // Production Mode: Real API call
      console.log("🚀 Production Mode: Calling real API")
      console.log("API URL:", getAPIUrl())

      const res = await fetch(`${getAPIUrl()}/create-payment-intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items, currency: 'usd' }),
      })

      console.log('Response status:', res.status)

      if (!res.ok) {
        const errorText = await res.text()
        console.error('Backend error:', errorText)
        throw new Error(`HTTP ${res.status}: ${errorText}`)
      }

      const data = await res.json()
      console.log('✅ Payment intent created:', data)
      setPaymentData(data)

      const { error } = await initPaymentSheet({
        paymentIntentClientSecret: data.clientSecret,
        merchantDisplayName: PAYMENT_CONFIG.MERCHANT_NAME,
        returnURL: getReturnUrl(),
      })

      if (!error) {
        console.log('✅ Stripe payment sheet initialized successfully')
        setReady(true)
      } else {
        console.error('❌ Stripe init error:', error)
        setError(`Stripe init error: ${error.message}`)
      }
    } catch (err: any) {
      console.error("❌ Payment initialization error:", err)
      setError(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const pay = async () => {
    // Production Mode: Real payment
    const { error } = await presentPaymentSheet()
    if (error) {
      Alert.alert('Payment failed', error.message)
    } else {
      clear()
      Alert.alert('Success', 'Payment complete')
      router.replace('/(tabs)')
    }
  }

  const retryPayment = () => {

    initializePayment()
  }

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20 }}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 10, textAlign: 'center' }}>
          Connecting to payment server...
        </Text>
      </View>
    )
  }

  if (error) {
    return (
      <ScrollView style={{ flex: 1, padding: 20 }}>
        <View style={{ alignItems: 'center', justifyContent: 'center', flex: 1 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10, color: 'red' }}>
            Payment Error
          </Text>
          <Text style={{ textAlign: 'center', marginBottom: 20 }}>
            {error}
          </Text>

          <View style={{ marginBottom: 20 }}>
            <Text style={{ fontWeight: 'bold', marginBottom: 10 }}>Debug Info:</Text>
            <Text>API URL: {getAPIUrl()}</Text>
            <Text>MVP Mode: OFF</Text>
            <Text>Items: {items.length}</Text>
            <Text>Total: ${(total / 100).toFixed(2)}</Text>
          </View>

          <Button title="Retry" onPress={retryPayment} />
          <View style={{ height: 10 }} />
          <Button title="Back to Cart" onPress={() => router.back()} />
        </View>
      </ScrollView>
    )
  }

  return (
    <ScrollView style={{ flex: 1, padding: 20 }}>
      <PaymentStatus />
      <View style={{ alignItems: 'center', justifyContent: 'center', flex: 1 }}>
        <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
          💳 Payment
        </Text>

        <View style={{ marginBottom: 20, width: '100%' }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10 }}>Order Summary:</Text>
          {items.map((item) => (
            <View key={item.id} style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 5 }}>
              <Text>{item.title} x{item.qty}</Text>
              <Text>${(item.priceInCents * item.qty / 100).toFixed(2)}</Text>
            </View>
          ))}
          <View style={{ borderTopWidth: 1, borderTopColor: '#ccc', marginTop: 10, paddingTop: 10 }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
              <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Total:</Text>
              <Text style={{ fontSize: 18, fontWeight: 'bold' }}>${(total / 100).toFixed(2)}</Text>
            </View>
          </View>
        </View>



        {ready ? (
          <Button
            title="Pay Now"
            onPress={pay}
            color="#007bff"
          />
        ) : (
          <Text>Initializing payment...</Text>
        )}

        <View style={{ height: 20 }} />
        <Button title="Back to Cart" onPress={() => router.back()} />
      </View>
    </ScrollView>
  )
}
