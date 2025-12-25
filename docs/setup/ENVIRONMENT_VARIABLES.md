# Environment Variables

Copy these to your `.env.local` file and fill in the values.

## Required Variables

```bash
# ============================================
# ABOUTAI ENVIRONMENT CONFIGURATION
# ============================================

# Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000

# --------------------------------------------
# DATABASE (Supabase)
# Get these from: https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
# --------------------------------------------
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# --------------------------------------------
# LLM PROVIDERS
# --------------------------------------------
# OpenAI: https://platform.openai.com/api-keys
OPENAI_API_KEY=

# Anthropic: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=

# --------------------------------------------
# TRUST ENGINE
# --------------------------------------------
TRUST_ENGINE_URL=http://localhost:8000
TRUST_ENGINE_API_KEY=

# Browserbase: https://browserbase.com/dashboard
BROWSERBASE_API_KEY=
BROWSERBASE_PROJECT_ID=

# --------------------------------------------
# QUEUE (Upstash Redis)
# Get these from: https://console.upstash.com
# --------------------------------------------
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# --------------------------------------------
# SEARCH (Algolia)
# Get these from: https://dashboard.algolia.com/account/api-keys
# --------------------------------------------
NEXT_PUBLIC_ALGOLIA_APP_ID=
NEXT_PUBLIC_ALGOLIA_SEARCH_KEY=
ALGOLIA_ADMIN_API_KEY=

# --------------------------------------------
# NEWSLETTER (Beehiiv)
# Get these from: https://app.beehiiv.com/settings/integrations
# --------------------------------------------
BEEHIIV_API_KEY=
BEEHIIV_PUBLICATION_ID=

# --------------------------------------------
# PAYMENTS (Stripe)
# Get these from: https://dashboard.stripe.com/apikeys
# --------------------------------------------
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

## Optional Variables

```bash
# --------------------------------------------
# AUTHENTICATION (Clerk - Optional)
# Get these from: https://dashboard.clerk.com
# --------------------------------------------
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
CLERK_WEBHOOK_SECRET=

# --------------------------------------------
# ANALYTICS (PostHog - Optional)
# Get these from: https://app.posthog.com/project/settings
# --------------------------------------------
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com

# --------------------------------------------
# ERROR TRACKING (Sentry - Optional)
# Get these from: https://sentry.io/settings/
# --------------------------------------------
SENTRY_DSN=
SENTRY_AUTH_TOKEN=
```

## Service Setup Links

| Service | Dashboard | Documentation |
|---------|-----------|---------------|
| Supabase | [supabase.com](https://supabase.com/dashboard) | [Docs](https://supabase.com/docs) |
| Vercel | [vercel.com](https://vercel.com/dashboard) | [Docs](https://vercel.com/docs) |
| Clerk | [clerk.com](https://dashboard.clerk.com) | [Docs](https://clerk.com/docs) |
| OpenAI | [platform.openai.com](https://platform.openai.com) | [Docs](https://platform.openai.com/docs) |
| Algolia | [algolia.com](https://dashboard.algolia.com) | [Docs](https://www.algolia.com/doc/) |
| Beehiiv | [beehiiv.com](https://app.beehiiv.com) | [Docs](https://developers.beehiiv.com) |
| Stripe | [stripe.com](https://dashboard.stripe.com) | [Docs](https://stripe.com/docs) |
| Upstash | [upstash.com](https://console.upstash.com) | [Docs](https://upstash.com/docs) |
| Browserbase | [browserbase.com](https://browserbase.com) | [Docs](https://docs.browserbase.com) |

