---
name: expense-log
description: Log daily spending to the xpenses MCP from a freeform recap of the user's day. Use whenever the user describes what they did, ate, bought, or where they went and it implies money spent — e.g. "log my day", "today I took the bus to Mahidol, ate breakfast, bought pizza", "spent 139 on pizza", "add my expenses", "log: bus 25, lunch at Big C", or any casual list of daily activities with costs. Trigger even if the user does not say the word "expense" or "log" — a recap of a day out almost always means expenses to record. Also handles explicit recurring-expense setup like "set up rent 4000/month" or "add a recurring 149 subscription every month". This skill knows the user's habitual prices, categories, and which account each thing comes from, fills gaps automatically, warns when a logged category nears its budget, and confirms the total before writing anything.
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
   - **TrueMoney** = everything from 7/11. Any 7/11 purchase (snacks, beer,
     drinks, bills paid at counter) logs to TrueMoney, never Cash.
   - **Cash** = buses/cycles, cheap street food (breakfast, dinner,
     rice+something), small snacks, coffee carts.
   - **KrungThai** (bank) = everything bigger: sit-down/branded food (Big C
     lunch, KFC, pizza, hotpot), clothes, tech, personal care, bills, rent,
     travel.
   - **SCB** = savings only. Never log daily spending here. Don't offer it as
     an expense account.
   - Clear by rule -> just use it and note which in the summary. Truly
     ambiguous -> ask.
   - **Exact account names** (pass these verbatim to `create_expense`):
     `KrungThai`, `Cash`, `SCB`, `TrueMoney`. No spaces in `TrueMoney`; the
     `K` in `KrungThai` is followed by a capital `T`.

4. **Default date = today (Bangkok).** If the user says "yesterday" or a date,
   use that. `create_expense` defaults to today already.

5. **One `create_expense` call per item.** Amounts are in **baht** (the tool
   converts). Keep the `note` short — just the item, with the meal/context in
   parens when useful: `bread (dinner)`, `rice + chicken (lunch)`, `bus`,
   `pizza`. Don't restate the account or "7/11"; the account already records
   where it came from. If the user gives their own parenthetical (a source or
   place like `powerbank (shopee)`, `case (lazada)`), keep it verbatim.

6. **Warn on budget only after writing, only for what you touched.** After the
   expenses are written, call `get_budgets` for the logged month and check the
   categories you logged this session. If any touched category is at or above
   **80%** of its limit, flag it in the final report. Ignore untouched
   categories and any category with no budget set. This is a heads-up, not a
   gate — never block or re-confirm because of budget.

7. **Recurring rules are explicit-only and expense-only.** Only create a
   recurring rule when the user asks for one in so many words ("set up rent
   4000/month", "recurring Claude sub 149 monthly"). Never infer a recurring
   rule from a normal daily recap. Only `type: expense` — this skill does not
   create recurring income or transfers.

## Habit map (the user's usual prices)

Prices are defaults — override whenever the user states a real number.

| Item (what user might type)        | Baht        | Category       | Account |
|------------------------------------|-------------|----------------|---------|
| breakfast                          | 20          | Groceries      | Cash    |
| dinner / night / night meal        | 20          | Groceries      | Cash    |
| rice + something / cheap street meal | ~30 (ask if unsure) | Groceries | Cash |
| Big C lunch (food)                 | 50          | Eating Out     | KrungThai |
| Big C lunch coffee                 | 5           | Coffee         | KrungThai |
| pizza                              | 139         | Eating Out     | KrungThai |
| hotpot / suki                      | 279         | Eating Out     | KrungThai |
| coffee (Taobin)                    | 5-10 (ask)  | Coffee         | KrungThai |
| coffee (branded cafe, e.g. Cafe Amazon) | ask    | Coffee         | KrungThai |
| coffee (street cart)               | 5-10 (ask)  | Coffee         | Cash    |
| bus to Mahidol                     | 25          | Transport      | Cash    |
| bus back / home from Mahidol       | 45          | Transport      | Cash    |
| other bus / cycle / songthaew      | ask (10-40) | Transport      | Cash    |
| 7/11 anything (snacks/beer/drinks) | ask         | Entertainment  | TrueMoney |
| taxi / airport / intercity trip    | ask         | Travel         | KrungThai |

Notes:
- **Bus to Mahidol is Transport, not the Mahidol category.** The `Mahidol`
  category is only for university costs — tuition, document/admin fees,
  academic supplies. Never route a bus fare there.
- Groceries here holds the cheap daily meals (breakfast, dinner, street food),
  by the user's budgeting convention. Branded/sit-down meals go to Eating Out.
- **All coffee goes to `Coffee`, always.** Every coffee is its own entry in
  the Coffee category — never fold it into Eating Out. Big C lunch splits into
  two entries: food 50 (Eating Out) + coffee 5 (Coffee). The user names the
  shop in parens (`coffee (Cafe Amazon)`, `coffee (Taobin)`) — keep it verbatim
  in the note. Taobin and branded cafes -> KrungThai; street cart -> Cash.

## Category guide for non-habit items

Map by the live category names from `get_categories`. Typical routing:

- **Clothing** — shirts, shoes, any apparel (KrungThai)
- **Personal Care** — perfume, skincare, toothbrush, soap, grooming (KrungThai)
- **Tech** — phone cases, screen glass, cables, gadgets (KrungThai)
- **Health** — pharmacy, meds, clinic (usually KrungThai)
- **Laundry** — wash/dry, laundromat, laundry service (Cash, or TrueMoney if 7/11-adjacent machine)
- **Bills** — mobile package, Claude subscription, any recurring service (KrungThai)
- **Rent** — monthly rent (KrungThai)
- **Mahidol** — university fees, documents, academic (account per size: KrungThai)
- **Other** — genuinely nothing fits; log here and tell the user to recategorize

Any item bought **at 7/11** overrides account to **TrueMoney** regardless of
category.

## Recurring expenses

Only when the user explicitly asks to set up a recurring/scheduled expense.
Parse: amount (baht), `interval_unit` (day/week/month) and `interval_count`
from the phrasing ("monthly" -> unit month, count 1; "every 2 weeks" -> unit
week, count 2; default count 1), category (live match), account (rule).

- **Always ask for `next_run_date`.** Never infer it silently. Confirm the
  YYYY-MM-DD date the schedule should first fire before creating.
- **Check for duplicates first.** Call `get_recurring`; if a rule with the same
  category/note/amount already exists, flag it in the confirm and let the user
  decide instead of blindly adding a second rule.
- **Schedule only — no back-charge.** Creating the rule does not log the
  current period. If the user also wants this month charged now, they must say
  so as a normal expense item.
- **Expense type only.** Use `create_recurring` with `type: expense`.

## Workflow

1. Call `get_categories` to load the live category list.
2. Parse the user's message into one-off expense items and any explicit
   recurring request. A message can contain both.
3. For each one-off item: assign amount (habit map or stated), category (live
   match), account (rule). Mark anything you had to guess. For a recurring
   request: derive amount, interval, category, account, and the (asked)
   next-run date; call `get_recurring` to check for a duplicate.
4. Show a summary. If there are recurring requests, split it into two sections:
   - **Expenses** — item | note | amount | category | account, plus the
     **total** and per-account subtotals. Flag any `Other` or guessed prices.
   - **Recurring** — amount | interval | next run | category | account, with a
     duplicate warning if one was found.
5. Ask any genuinely ambiguous questions (unknown price, coin-flip account,
   the recurring next-run date) in one batch — don't nickel-and-dime the user.
6. On one confirmation, write everything: `create_expense` once per one-off
   item, `create_recurring` once per recurring rule.
7. After writing, call `get_budgets` for the logged month and check the
   categories you touched. Report what was written (count + total), then flag
   any touched category at or above 80% of its limit. Keep it short; skip
   categories with no budget.

## Example

**Input:**
> today breakfast, bus to mahidol and back, big c lunch, 7/11 beer 60, pizza for dinner

**Parsed summary shown to user:**

| Item              | Note                | Baht | Category      | Account    |
|-------------------|---------------------|------|---------------|------------|
| breakfast         | breakfast         | 20   | Groceries     | Cash       |
| bus to Mahidol    | bus (Mahidol)     | 25   | Transport     | Cash       |
| bus home          | bus (home)        | 45   | Transport     | Cash       |
| Big C lunch       | Big C (lunch)     | 55   | Eating Out    | KrungThai  |
| 7/11 beer         | beer (snack)      | 60   | Entertainment | TrueMoney  |
| pizza             | pizza (dinner)    | 139  | Eating Out    | KrungThai  |

Total: **344 baht** (Cash 90, KrungThai 194, TrueMoney 60). Confirm to log?
Then write 6 entries.
