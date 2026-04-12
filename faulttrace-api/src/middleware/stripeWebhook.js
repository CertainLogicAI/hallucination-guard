const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const crypto = require('crypto');

/**
 * Middleware for Stripe webhook signature verification.
 * Consumes raw body, verifies Stripe-Signature header.
 */
function stripeWebhook(req, res, next) {
  const sig = req.headers['stripe-signature'];
  const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!sig || !endpointSecret) {
    console.error('Stripe webhook: missing signature or secret');
    return res.status(400).json({ error: 'Missing signature or webhook secret' });
  }

  try {
    // Verify signature; req.rawBody must be set by body parser with raw option
    const event = stripe.webhooks.constructEvent(req.rawBody, sig, endpointSecret);
    req.stripeEvent = event;
    next();
  } catch (err) {
    console.error('Stripe webhook signature verification failed:', err.message);
    return res.status(400).json({ error: 'Webhook signature verification failed' });
  }
}

module.exports = {
  stripeWebhook
};
