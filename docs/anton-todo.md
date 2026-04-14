# Anton's To-Do List
*Things that require Anton's accounts, credentials, or decisions*

## Socials to Set Up
- [x] **X (Twitter)** — @CertainLogicAI locked in. Update bio, display name, pfp. Connect API once X API keys are ready.
- [ ] **LinkedIn** — check if CertainLogic company page name is available. Create it. Personal profile as Anton is the credibility anchor.
- [ ] **YouTube** — claim channel now even if not posting yet. Protect the brand name.

## Credentials Needed
- [ ] **X API tokens** — go to developer.twitter.com, regenerate Access Token + Access Token Secret together. Provide all 4 values: API Key, API Secret, Access Token, Access Token Secret.
- [x] **OpenRouter API key** — configured and working. 24 free models available.
- [ ] **Stripe account** — set up at stripe.com (needs identity verification, ~15 min). Needed for CertainLogic.ai shop.

## GitHub / Cloudflare (for site launch)
- [ ] **Create GitHub repo** — github.com/new → name: `certainlogic-site` → private
- [ ] **Push site code** — I can do this if you give me a GitHub personal access token, or you can run:
  ```
  cd /data/.openclaw/workspace/certainlogic-site
  git remote add origin https://github.com/YOUR_USERNAME/certainlogic-site.git
  git branch -M main
  git push -u origin main
  ```
- [ ] **Connect Cloudflare Pages** — dashboard → Pages → Create project → Connect Git → select repo → build: `npm run build` → output: `dist`
- [ ] **Add custom domain** — certainlogic.ai in Cloudflare Pages settings

## Business Decisions Pending
- [ ] **Finalize FaultTrace pricing** — Anton still working it out. Range discussed: $99-499/mo tiers.
- [ ] **IP attorney consult** — ~$500, review patent claims before month 6 deadline. Not urgent yet.

## Accounts to Migrate (once Stripe is live)
- [ ] Move Gumroad products → CertainLogic.ai shop
- [ ] Redirect ShopClawMart.com → certainlogic.ai/shop
- [ ] Update ClawHub @blenderism profile to link CertainLogic.ai
