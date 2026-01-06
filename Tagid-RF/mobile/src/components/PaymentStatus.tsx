// src/components/PaymentStatus.tsx
import { getAPIUrl, isMVPMode } from '@/src/config/payment';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function PaymentStatus() {
  if (!__DEV__) return null; // Only show in development

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔧 Debug Info</Text>
      <Text style={styles.info}>Mode: {isMVPMode() ? '🎭 MVP' : '🚀 Production'}</Text>
      <Text style={styles.info}>API: {getAPIUrl()}</Text>
      <Text style={styles.info}>Stripe: {isMVPMode() ? 'Mock' : 'Real'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f8f9fa',
    padding: 10,
    margin: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  title: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#6c757d',
  },
  info: {
    fontSize: 10,
    color: '#6c757d',
    marginBottom: 2,
  },
});
