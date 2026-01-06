// src/screens/CartScreen.tsx
import { useCart } from '@/src/store/cart'
import { router } from 'expo-router'
import { Button, FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native'

export default function CartScreen() {
  const { items, inc, dec } = useCart()
  const total = items.reduce((s, it) => s + it.priceInCents * it.qty, 0)

  console.log('🛒 Cart items:', items)
  console.log('💰 Cart total:', total, 'cents')

  if (items.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>🛒</Text>
        <Text style={styles.emptyTitle}>Your cart is empty</Text>
        <Text style={styles.emptySubtitle}>Scan items to add them to your cart</Text>
        <View style={styles.emptyButton}>
          <Button 
            title="Start Scanning" 
            onPress={() => router.push('/(tabs)')} 
          />
        </View>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={items}
        keyExtractor={(x) => x.id}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <View style={styles.cartItem}>
            <View style={styles.itemImage}>
              <Text style={styles.itemEmoji}>📦</Text>
            </View>
            
            <View style={styles.itemDetails}>
              <Text style={styles.itemTitle}>{item.title}</Text>
              <Text style={styles.itemPrice}>
                ${(item.priceInCents/100).toFixed(2)} each
              </Text>
            </View>
            
            <View style={styles.quantityControls}>
              <TouchableOpacity 
                style={[
                  styles.quantityButton, 
                  item.qty === 1 && styles.quantityButtonRemove
                ]} 
                onPress={() => dec(item.id)}
              >
                <Text style={styles.quantityButtonText}>
                  {item.qty === 1 ? '🗑️' : '−'}
                </Text>
              </TouchableOpacity>
              
              <Text style={styles.quantityText}>{item.qty}</Text>
              
              <TouchableOpacity 
                style={styles.quantityButton} 
                onPress={() => inc(item.id)}
              >
                <Text style={styles.quantityButtonText}>+</Text>
              </TouchableOpacity>
            </View>
            
            <Text style={styles.itemTotal}>
              ${(item.priceInCents * item.qty / 100).toFixed(2)}
            </Text>
          </View>
        )}
      />
      
      <View style={styles.footer}>
        <View style={styles.totalRow}>
          <Text style={styles.totalLabel}>Total:</Text>
          <Text style={styles.totalAmount}>${(total/100).toFixed(2)}</Text>
        </View>
        <Button 
          title="Proceed to Payment" 
          onPress={() => router.push('/pay')}
          color="#007AFF"
        />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  listContent: {
    padding: 16,
  },
  cartItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  itemImage: {
    width: 60,
    height: 60,
    backgroundColor: '#F0F0F0',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  itemEmoji: {
    fontSize: 32,
  },
  itemDetails: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    color: '#333',
  },
  itemPrice: {
    fontSize: 14,
    color: '#666',
  },
  quantityControls: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
  },
  quantityButton: {
    width: 32,
    height: 32,
    backgroundColor: '#007AFF',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantityButtonRemove: {
    backgroundColor: '#FF3B30',
  },
  quantityButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  quantityText: {
    fontSize: 16,
    fontWeight: '600',
    marginHorizontal: 12,
    minWidth: 30,
    textAlign: 'center',
  },
  itemTotal: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    minWidth: 60,
    textAlign: 'right',
  },
  footer: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    paddingVertical: 8,
  },
  totalLabel: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: '700',
    color: '#007AFF',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F5F5F5',
  },
  emptyIcon: {
    fontSize: 80,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    textAlign: 'center',
  },
  emptyButton: {
    width: 200,
  },
});
