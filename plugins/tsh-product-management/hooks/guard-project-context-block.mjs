#!/usr/bin/env node
/**
 * PreToolUse guard for the `tsh:project-context` block in CLAUDE.md and
 * CLAUDE.local.md.
 *
 * The block tells every session in a code repository where the project's
 * knowledge base is and which skill reads it. An agent asked to shorten or tidy
 * CLAUDE.md removes it as readily as any other paragraph, and the explicit "never
 * remove" in its own text is a request, not a control. This makes it one: an Edit
 * or Write whose result no longer contains the block, byte for byte, is denied.
 *
 * Cost: hooks.json runs this only for Edit and Write on a file named CLAUDE.md or
 * CLAUDE.local.md (the `if` filter), so any other edit never starts a process.
 *
 * What it does not cover: a shell command that rewrites the file (`sed -i`, `>`).
 * The locator reports a missing or changed block on the next read and offers to
 * restore it. Init writes the block through its own script, never through Edit or
 * Write, so it is never blocked here.
 *
 * Contract: reads the PreToolUse payload as JSON on stdin; emits a deny decision
 * as JSON on stdout, or stays silent (exit 0) so normal permission rules apply.
 * Any error inside the hook allows the call: a broken guard must not lock people
 * out of their own CLAUDE.md.
 */

import { readFileSync } from "node:fs";

const BLOCK = /<!-- tsh:project-context START[\s\S]*?<!-- tsh:project-context END -->/;

function deny(reason) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: reason,
      },
    })
  );
  process.exit(0);
}

function replaceOnce(text, oldString, newString, all) {
  return all ? text.split(oldString).join(newString) : text.replace(oldString, () => newString);
}

function resultOf(tool, input, current) {
  if (tool === "Write") return input.content ?? "";
  if (tool === "Edit") return replaceOnce(current, input.old_string ?? "", input.new_string ?? "", input.replace_all);
  if (tool === "MultiEdit") {
    return (input.edits ?? []).reduce(
      (text, e) => replaceOnce(text, e.old_string ?? "", e.new_string ?? "", e.replace_all),
      current
    );
  }
  return null;
}

try {
  const payload = JSON.parse(readFileSync(0, "utf8"));
  const input = payload.tool_input ?? {};
  const path = input.file_path ?? "";
  if (!/(^|\/)CLAUDE(\.local)?\.md$/.test(path)) process.exit(0);
  let current;
  try {
    current = readFileSync(path, "utf8");
  } catch {
    process.exit(0); // a new file has no block to protect
  }
  const block = current.match(BLOCK);
  if (!block) process.exit(0);
  const next = resultOf(payload.tool_name, input, current);
  if (next !== null && !next.includes(block[0])) {
    deny(
      "The tsh:project-context block in this file is protected: no agent removes or edits it. " +
        "Keep it exactly as it is and change only the rest of the file. To change the block itself, " +
        "the person runs /tsh-product-management:initializing-project-context."
    );
  }
} catch {
  // fall through: allow
}
process.exit(0);
