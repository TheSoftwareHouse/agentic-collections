#!/usr/bin/env bash
# A small orders service: the plan must use the commands package.json really has.
set -euo pipefail
mkdir -p src test
cat > package.json <<'JSON'
{
  "name": "orders-service",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test test/",
    "lint": "eslint src test",
    "typecheck": "tsc --noEmit"
  }
}
JSON
cat > CLAUDE.md <<'MD'
# orders-service

HTTP service for customer orders. Node 24, TypeScript, node:test.

- Run the tests with `npm test`, lint with `npm run lint`, typecheck with `npm run typecheck`.
- Routes live in `src/routes.ts`, persistence in `src/orders.ts`.
MD
cat > src/orders.ts <<'TS'
export type OrderStatus = "placed" | "shipped" | "delivered";
export interface Order { id: string; customerId: string; status: OrderStatus; placedAt: Date }
const orders = new Map<string, Order>();
export function findOrder(id: string): Order | undefined { return orders.get(id); }
export function saveOrder(order: Order): void { orders.set(order.id, order); }
TS
cat > src/routes.ts <<'TS'
import { findOrder } from "./orders.js";
export function getOrder(id: string) {
  const order = findOrder(id);
  return order ? { status: 200, body: order } : { status: 404 };
}
TS
cat > test/orders.test.ts <<'TS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { saveOrder, findOrder } from "../src/orders.js";
test("finds a saved order", () => {
  saveOrder({ id: "o1", customerId: "c1", status: "placed", placedAt: new Date() });
  assert.equal(findOrder("o1")?.status, "placed");
});
TS
