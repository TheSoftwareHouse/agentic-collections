#!/usr/bin/env bash
# An invoices service with one planted object-level authorization flaw (IDOR) in
# src/routes/invoices.js; src/routes/orders.js does the ownership check correctly.
set -euo pipefail
mkdir -p src/routes src/middleware
cat > package.json <<'JSON'
{
  "name": "billing-api",
  "private": true,
  "type": "module",
  "scripts": { "start": "node src/app.js", "test": "node --test" },
  "dependencies": { "express": "4.21.2" }
}
JSON
cat > CLAUDE.md <<'MD'
# billing-api

Express service. Every route under /api requires a logged-in user (`requireUser`),
which sets `req.user.id`. Customers may only see their own invoices and orders.
MD
cat > src/middleware/auth.js <<'JS'
export function requireUser(req, res, next) {
  if (!req.session?.userId) return res.status(401).end();
  req.user = { id: req.session.userId };
  next();
}
JS
cat > src/db.js <<'JS'
export const db = {
  invoices: { findById: async (id) => null },
  orders: { findById: async (id) => null },
};
JS
cat > src/routes/orders.js <<'JS'
import { Router } from "express";
import { db } from "../db.js";
import { requireUser } from "../middleware/auth.js";

export const orders = Router();

orders.get("/orders/:id", requireUser, async (req, res) => {
  const order = await db.orders.findById(req.params.id);
  if (!order || order.customerId !== req.user.id) return res.status(404).end();
  res.json(order);
});
JS
cat > src/routes/invoices.js <<'JS'
import { Router } from "express";
import { db } from "../db.js";
import { requireUser } from "../middleware/auth.js";

export const invoices = Router();

invoices.get("/invoices/:id", requireUser, async (req, res) => {
  const invoice = await db.invoices.findById(req.params.id);
  if (!invoice) return res.status(404).end();
  res.json(invoice);
});
JS
cat > src/app.js <<'JS'
import express from "express";
import { orders } from "./routes/orders.js";
import { invoices } from "./routes/invoices.js";

const app = express();
app.use("/api", orders);
app.use("/api", invoices);
app.listen(3000);
JS
