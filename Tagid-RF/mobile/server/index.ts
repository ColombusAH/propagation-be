import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import Stripe from "stripe";

// Load environment variables
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Initialize Stripe with secret key
const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
if (!stripeSecretKey) {
  console.error("❌ STRIPE_SECRET_KEY is not set in environment variables");
  console.error("Please create a .env file with your Stripe secret key");
  process.exit(1);
}

const stripe = new Stripe(stripeSecretKey);

app.post("/create-payment-intent", async (req, res) => {
  console.log("create-payment-intent", req.body);
  // req.body = { items: [{id, qty, priceInCents}], currency: "usd" }
  const { items, currency = "usd" } = req.body;

  // Validate items
  if (!items || !Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ error: "Items array is required and cannot be empty" });
  }

  // In real life, re-price on server using product IDs.
  const amount = items.reduce((sum: number, it: { priceInCents: number; qty: number }) => sum + it.priceInCents * it.qty, 0);

  // Validate amount
  if (amount <= 0) {
    return res.status(400).json({ error: "Invalid amount" });
  }

  try {
    const pi = await stripe.paymentIntents.create({
      amount,
      currency,
      automatic_payment_methods: { enabled: true },
    }); // Return client secret
    res.json({ clientSecret: pi.client_secret });
  } catch (e) {
    console.error("Stripe error:", e);
    res.status(500).json({ error: "Stripe error" });
  }
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`🚀 API server running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`💳 Stripe integration: ${stripeSecretKey.startsWith('sk_test_') ? 'TEST MODE' : 'LIVE MODE'}`);
});