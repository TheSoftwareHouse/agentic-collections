# The inventory sweep

Use this reference when any task changes a contract — a schema, a shared type, an
API response, an event payload, an enum. It finds the call sites a name search
cannot.

## Why a name search is not enough

A contract change breaks two kinds of call sites. The ones that *use* the contract
are findable by grepping its name — the task-sizing rule covers those. Enumerating
inventories are not: a migration ledger, an `information_schema` column list, a
deep-equality response fixture, an allowlist — each names every **existing** member
and never the new one, so no search for the new contract's name can hit them.

Worse, the tier system hides them. An inventory in an e2e or integration suite is
invisible to the task tier and every phase checkpoint — those tiers never run it —
so a miss surfaces in the final verification phase, the most expensive moment a
plan can learn about a file it forgot. Plan-time search by *inventory pattern* is
the only defense that exists.

## The sweep

Search by change type, across every test tier — unit, integration, e2e — plus
fixtures and fake servers:

| Change | Search for |
| --- | --- |
| DB column, table, or migration | `information_schema`, physical-order reads (`ordinal_position`), migration-name ledgers, `toEqual([` over test directories |
| API response or payload field | the endpoint path in e2e specs and in fake-server fixtures that replay its responses |
| Widened or narrowed shared type | object-literal constructors of the type in specs, harnesses, and seed data |
| Enum member, status, or event type | exhaustive switch/map assertions and allowlists enumerating the current members |

## Closing the hits

Close every hit in the plan, one of two ways: the file joins the owning task's
`**Files:**` list, or the plan records it as checked and unaffected — one line
naming the file and why the change cannot reach it. A hit closed neither way is a
failed gate one tier later, in a file no delegate owns.
