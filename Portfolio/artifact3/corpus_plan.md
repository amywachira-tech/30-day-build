# Artifact #3: Corpus Plan (Kestrel Home)

18 sources. The key facts are the ground truth for the eval, so each document must state them exactly and nothing that contradicts them.

**Policy areas:** returns, shipping, identity, warranty, payments, escalation, fraud
**Owners:** finance, operations, legal, support
**Tiers:** 1 = announcement (Slack #policy-updates or Legal email), 2 = Confluence handbook, 3 = Google Doc

**Data model changes:** add `support` as an owner, add `escalation` and `fraud` as policy areas, add an optional `expires_on` field for announcements. Expired announcements are excluded from search.

---

## Returns

| # | Source | Tier | Owner | Access | Trap | Key facts |
|---|---|---|---|---|---|---|
| 1 | Returns FAQ | 3 | finance | agent | Superseded across tiers | All items, including sale items, returnable within 60 days of delivery. Last modified Aug 2025. |
| 2 | #policy-updates: Sale item returns | 1 | finance | agent | First of two announcements | Effective **Feb 3, 2026**: sale items returnable within **30 days** of delivery (previously 60). Standard items unchanged at 60 days. |
| 3 | #policy-updates: Clearance items | 1 | finance | agent | Later same-owner announcement wins | Effective **Jun 16, 2026**: items tagged "Final Clearance" are final sale with no returns. Other sale items stay at 30 days. |
| 4 | Returns and Refunds Handbook | 2 | finance | mixed | Mixed access; updated after February but not after June, so it says nothing about clearance | **Agent section:** standard items 60 days, sale items 30 days. Refund to original payment method within 5 to 7 business days. Agents approve refunds up to **$150**. **Lead section:** leads approve **$150.01 to $1,000**. Above $1,000 needs the Finance manager. Leads may give goodwill credit up to $50. |
| 5 | Refund Approval Guide | 3 | finance | lead | Lead-only; used for the lead-user success test | Same thresholds as the lead section of #4: leads approve $150.01 to $1,000, Finance manager above $1,000. |
| 6 | Damaged Item Policy (Kestrel-sold items) | 2 | operations | agent | Wrong-rule trap with #7 | Kestrel-sold items: report damage within **14 days** of delivery with a photo. Kestrel refunds or replaces immediately. No return needed for items under **$75**. |
| 7 | Marketplace Seller Returns Policy | 2 | operations | agent | Wrong-rule trap with #6 | Items sold by marketplace sellers: customer reports damage within **7 days** with photos. Claim goes to the seller through Seller Hub. Kestrel refunds only if the seller has not responded within **3 business days**. |

## Fraud and escalation

| # | Source | Tier | Owner | Access | Trap | Key facts |
|---|---|---|---|---|---|---|
| 8 | Fraud and Serial-Returner Signals | 2 | finance | lead | Most sensitive lead-only content; must never reach an agent | Flag an account with 4 or more returns in 90 days, return value above 60% of spend in 12 months, or 2 or more "item not received" claims in 6 months. All refunds on flagged accounts need lead approval whatever the amount. Never tell the customer the account is flagged. |
| 9 | Escalation Matrix | 2 | support | agent | Normal | Refunds above $150 go to a lead. Any account showing a fraud flag goes to a lead. Data deletion and privacy requests go to a lead, who forwards them to Legal. Damaged items over $500 go to a lead. |

## Identity verification

| # | Source | Tier | Owner | Access | Trap | Key facts |
|---|---|---|---|---|---|---|
| 10 | Identity Verification FAQ | 3 | legal | agent | Stale policy with misleading `last_modified` | Policy dated **Mar 2024**: verify with full name and order number, then order status, tracking and delivery address may be shared. `last_modified` **Sep 28, 2026** (typo fix). |
| 11 | Customer Identity Verification | 2 | legal | agent | Current handbook procedure | Verify with full name, the email on the account, and one of: last 4 digits of the payment card or the billing postcode. An order number alone is never enough. Never read out the full delivery address; the city may be confirmed. If verification fails, share no order details; offer to send the information to the email on file. |
| 12 | Legal email: Identity verification requirements | 1 | legal | agent | Confirms #11; tier 1 | Effective **Jul 21, 2026**. Same requirements as #11. Adds: if the caller cannot give the account email, do not give tracking by phone; send the tracking link to the account email instead. |

## Shipping

| # | Source | Tier | Owner | Access | Trap | Key facts |
|---|---|---|---|---|---|---|
| 13 | Shipping and Delivery Handbook | 2 | operations | agent | Normal | Standard parcels 3 to 5 business days. Freight (large furniture) 7 to 14 business days. A shipment is lost after **10 business days** with no carrier scan movement. Once lost, reship or refund. |
| 14 | Carrier Escalation Guide | 2 | operations | mixed | Mixed access | **Agent section:** open a carrier trace after 5 business days with no movement. **Lead section:** leads may authorize a reship before loss is confirmed on orders under $300. |
| 15 | #policy-updates: Freight delays | 1 | operations | agent | Cross-tier override that applies to freight only | Effective **Oct 1 to Nov 15, 2026** (`expires_on` Nov 15): freight is considered lost after **15 business days** instead of 10. Standard parcels unchanged. |

## Warranty and payments

| # | Source | Tier | Owner | Access | Trap | Key facts |
|---|---|---|---|---|---|---|
| 16 | Warranty Claims FAQ | 3 | operations | agent | Same-tier conflict with #17 | Furniture: 2-year warranty on structural defects. Appliances: **1 year**. Proof of purchase required. Wear and tear excluded. |
| 17 | Appliance Warranty Notes | 3 | operations | agent | Same-tier conflict with #16; should produce "ask a lead" | Appliances: **2 years**. No date stated. |
| 18 | Payment Dispute Playbook | 3 | finance | lead | Blocked for agents | Duplicate charges, including Klarna: lead confirms in the payment dashboard and refunds the duplicate within 24 hours. Chargeback responses within 7 days. Never admit liability in writing. |

---

## Deliberately not covered

No source mentions **gift cards** or **international shipping**. Use one of these for the unanswerable eval question.

## Trap coverage check

| Trap | Rows |
|---|---|
| Superseded across tiers | 1 vs 2, 3, 4 |
| Two announcements, later wins | 2 vs 3 |
| Handbook partially updated | 4 vs 3 (clearance) |
| Stale procedure with misleading date | 10 vs 11, 12 |
| Wrong rule applied | 6 vs 7 |
| Same-tier conflict, ask a lead | 16 vs 17 |
| Cross-tier override, partial scope | 13 vs 15 |
| Mixed-access page | 4, 14 |
| Lead-only, blocked for agents | 5, 8, 18 |
| Lead user succeeds | 5 or 4 (lead section) |
| Unanswerable | Gift cards or international shipping |
