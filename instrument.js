// Initialize Sentry as early as possible in the Node process.
const Sentry = require("@sentry/node");

Sentry.init({
  dsn: "https://b84a0c4beaff142fadb5d86ea64d5584@o4510636967460864.ingest.us.sentry.io/4510647563386880",
  // Capture 100% of transactions in dev; tune down in production.
  tracesSampleRate: 1.0,
  // Enable sending default PII such as client IPs for richer event context.
  sendDefaultPii: true,
});

module.exports = { Sentry };
