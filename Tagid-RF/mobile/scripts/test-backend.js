// scripts/test-backend.js
// Simple script to test if the backend is working

const API_URL = 'http://localhost:3002';

async function testBackend() {
  console.log('🧪 Testing backend connection...');
  
  try {
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const healthResponse = await fetch(`${API_URL}/health`);
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('✅ Health check passed:', healthData);
    } else {
      throw new Error(`Health check failed: ${healthResponse.status}`);
    }

    // Test payment intent creation
    console.log('2. Testing payment intent creation...');
    const testItems = [
      { id: 'test-item', title: 'Test Item', priceInCents: 1000, qty: 1 }
    ];
    
    const paymentResponse = await fetch(`${API_URL}/create-payment-intent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: testItems, currency: 'usd' }),
    });

    if (paymentResponse.ok) {
      const paymentData = await paymentResponse.json();
      console.log('✅ Payment intent created successfully');
      console.log('   Client Secret:', paymentData.clientSecret ? 'Present' : 'Missing');
    } else {
      const errorData = await paymentResponse.json();
      throw new Error(`Payment intent failed: ${errorData.error}`);
    }

    console.log('🎉 All backend tests passed!');
    
  } catch (error) {
    console.error('❌ Backend test failed:', error.message);
    console.log('\n💡 Troubleshooting:');
    console.log('1. Make sure the backend server is running: npm run server');
    console.log('2. Check if port 3002 is available');
    console.log('3. Verify your .env file has STRIPE_SECRET_KEY set');
    process.exit(1);
  }
}

testBackend();
