---
name: expense-log
description: Log daily spending to the xpenses MCP from a freeform recap of the user's day. Use whenever the user describes what they did, ate, bought, or where they went and it implies money spent — e.g. "log my day", "today I took the bus to Mahidol, ate breakfast, bought pizza", "spent 139 on pizza", "add my expenses", "log: bus 25, lunch at Big C", or any casual list of daily activities with costs. Trigger even if the user does not say the word "expense" or "log" — a recap of a day out almost always means expenses to record. This skill knows the user's habitual prices, categories, and which account each thing comes from, fills gaps automatically, and confirms the total before writing anything.
---

# Expense Log

Turn a freeform recap of the user's day into correctly-categorized expense
entries in the xpenses MCP. The user types what they did in plain language;
this skill parses each item, fills in known prices, picks the right category
and account, shows a summary, and writes only after the user confirms.

## Core rules (why they matter)

1. **Read categories live first, every session.** Categories change and this
   skill must never guess against a stale list. Call `get_categories` before
   mapping anything. Match item -> category by the live names only. **Never
   create or edit a category** — if nothing fits, use `Other` and flag it so
   the user can fix it later. Silent miscategorization corrupts the budgets we
   built the whole system around.

2. **Fill known prices, then confirm the total.** The user logs fast and
   sloppy ("breakfast, bus to Mahidol, pizza"). Auto-fill habitual prices from
   the table below so they don't have to type numbers, but always show the
   parsed list + total and wait for a "yes" before writing. A wrong assumed
   price is worse than asking, so the confirm step is non-negotiable.

3. **Pick the account by rule, ask only on a genuine coin-flip.**
   - **Cash** = buses/cycles, 7/11, cheap street food (breakfast, dinner,
     rice+something), small snacks, coffee carts.
   - **Next** (bank) = everything bigger: sit-down/branded food (Big C lunch,
     KFC, pizza, hotpot), clothes, tech, personal care, bills, rent, travel.
   - Clear by rule -> just use it and note which in the summary. Truly
     ambiguous -> ask.

4. **Default date = today (Bangkok).** If the user says "yesterday" or a date,
   use that. `create_expense` defaults to today already.

5. **One `create_expense` call per item.** Amounts are in **baht** (the tool
   converts). Put the specific place/detail in the `note` (e.g. "Bus to
   Mahidol", "Pizza", "Big C lunch") so history stays readable.

## Habit map (the user's usual prices)

Prices are defaults — override whenever the user states a real number.

| Item (what user might type)        | Baht        | Category       | Account |
|------------------------------------|-------------|----------------|---------|
| breakfast                          | 20          | Groceries      | Cash    |
| dinner / night / night meal        | 20          | Groceries      | Cash    |
| rice + something / cheap street meal | ~30 (ask if unsure) | Groceries | Cash |
| Big C lunch                        | 55 (50 + 5 coffee) | Eating Out | Next |
| pizza                              | 139         | Eating Out     | Next    |
| hotpot / suki                      | 279         | Eating Out     | Next    |
| coffee (Taobin / cart)             | 5-10 (ask)  | Eating Out     | Cash    |
| bus to Mahidol                     | 25          | Transport      | Cash    |
| bus back / home from Mahidol       | 45          | Transport      | Cash    |
| other bus / cycle / songthaew      | ask (10-40) | Transport      | Cash    |
| 7/11 snacks / beer                 | ask         | Entertainment  | Cash    |
| taxi / airport / intercity trip    | ask         | Travel         | Next    |

Notes:
- **Bus to Mahidol is Transport, not the Mahidol category.** The `Mahidol`
  category is only for university costs — tuition, document/admin fees,
  academic supplies. Never route a bus fare there.
- Groceries here holds the cheap daily meals (breakfast, dinner, street food),
  by the user's budgeting convention. Branded/sit-down meals go to Eating Out.

## Category guide for non-habit items

Map by the live category names from `get_categories`. Typical routing:

- **Clothing** — shirts, shoes, any apparel (Next)
- **Personal Care** — perfume, skincare, toothbrush, soap, grooming (Next)
- **Tech** — phone cases, screen glass, cables, gadgets (Next)
- **Health** — pharmacy, meds, clinic (usually Next)
- **Bills** — mobile package, Claude subscription, any recurring service (Next)
- **Rent** — monthly rent (Next)
- **Mahidol** — university fees, documents, academic (account per size: Next)
- **Other** — genuinely nothing fits; log here and tell the user to recategorize

## Workflow

1. Call `get_categories` to load the live category list.
2. Parse the user's recap into discrete items.
3. For each item: assign amount (habit map or stated), category (live match),
   account (rule). Mark anything you had to guess.
4. Show a summary table: item | note | amount | category | account, plus the
   **total** and per-account subtotals. Flag any `Other` or guessed prices.
5. Ask any genuinely ambiguous questions (unknown price, coin-flip account) in
   one batch — don't nickel-and-dime the user with one question at a time.
6. On confirmation, call `create_expense` once per item.
7. Report what was written (count + total). Optionally note if any category is
   now near its monthly budget, but keep it short.

## Example

**Input:**
> today breakfast, bus to mahidol and back, big c lunch, bought a phone cable 90, pizza for dinner

**Parsed summary shown to user:**

| Item              | Note                | Baht | Category    | Account |
|-------------------|---------------------|------|-------------|---------|
| breakfast         | breakfast           | 20   | Groceries   | Cash    |
| bus to Mahidol    | Bus to Mahidol      | 25   | Transport   | Cash    |
| bus home          | Bus back from Mahidol | 45 | Transport   | Cash    |
| Big C lunch       | Big C lunch         | 55   | Eating Out  | Next    |
| phone cable       | Phone cable         | 90   | Tech        | Next    |
| pizza             | Pizza               | 139  | Eating Out  | Next    |

Total: **374 baht** (Cash 90, Next 284). Confirm to log? Then write 6 entries.
