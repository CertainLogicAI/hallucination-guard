const router = require('express').Router();
const fs = require('fs');
const path = require('path');

/**
 * POST /webhooks/stripe
 * Handle Stripe webhook events
 *
 * Middleware chain: express.raw() → stripeWebhook() → this router
 * Expects JSON payload with Stripe-Signature header.
 */
router.post('/stripe', async (req, res, next) => {
  const event = req.stripeEvent;

  // Basic logging
  console.log(`[Stripe] ${event.type} - ${event.id}`);

  // Persist event to file (append-only JSONL)
  // In production, use a database; this is a simple dev log.
  const logLine = JSON.stringify({
    id: event.id,
    type: event.type,
    created: event.created,
    data: event.data.object
  }) + '\n';

  const logPath = path.join(__dirname, '../../webhook-events.jsonl');
  try {
    fs.appendFileSync(logPath, logLine, 'utf8');
  } catch (err) {
    console.error('Failed to write webhook log:', err.message);
    // Continue anyway; just a logging failure
  }

  // Handle specific event types (placeholder for future DB integration)
  switch (event.type) {
    case 'checkout.session.completed':
      // TODO: Mark customer as active, record subscription details
      console.log('  → Subscription purchased:', event.data.object.customer);
      break;
    case 'customer.subscription.updated':
      // TODO: Update subscription status (canceled, past_due, etc.)
      console.log('  → Subscription updated:', event.data.object.status);
      break;
    case 'customer.subscription.deleted':
      // TODO: Revoke API key or mark account inactive
      console.log('  → Subscription deleted:', event.data.object.customer);
      break;
    default:
      // Unhandled event types are still logged
      break;
  }

  // Respond quickly to Stripe (they expect <2s)
  res.status(200).json({ received: true });
});

module.exports = router;
