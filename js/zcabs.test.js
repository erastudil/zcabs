// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import test from "node:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import {
  FORMAT_TEMPLATE,
  createFsIO,
  createHarness,
  createMemoryIO,
  emitLook,
  formatSpoken,
  look,
  mint,
  observe,
  parseLookBlock,
  rotate,
  verify,
} from "./zcabs.js";

test("emitLook has template not a value", () => {
  const block = emitLook("store/f_abc.dat");
  assert.equal(block.includes("LOOK: store/f_abc.dat"), true);
  assert.equal(block.includes(FORMAT_TEMPLATE), true);
});

test("mint look observe verify rotate", () => {
  const store = mint();
  const block = look(store, "identity");
  const pair = observe(store, "identity");
  assert.equal(block.includes(String(pair.integer)), false);
  assert.equal(block.includes(FORMAT_TEMPLATE), true);
  const spoken = formatSpoken(pair.string, pair.integer);
  assert.equal(verify(store, spoken, "identity").ok, true);
  assert.equal(verify(store, formatSpoken(pair.string, pair.integer + 1), "identity").ok, false);
  assert.equal(verify(store, `tests passed ${pair.integer}`, "identity").ok, false);
  const old = observe(store, "canary");
  rotate(store, "canary");
  const next = observe(store, "canary");
  assert.notEqual(old.integer, next.integer);
  assert.equal(verify(store, formatSpoken(old.string, old.integer), "canary").ok, false);
  assert.equal(verify(store, formatSpoken(next.string, next.integer), "canary").ok, true);
});

test("unknown key does not list", () => {
  const store = mint();
  assert.throws(() => observe(store, "nope"), /unknown key/);
});

test("two mints differ", () => {
  const a = observe(mint(), "identity").integer;
  const b = observe(mint(), "identity").integer;
  assert.notEqual(a, b);
});

test("fs io roundtrip", () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), "zcabs-js-"));
  try {
    const io = createFsIO(fs, path, home);
    const store = mint({ io });
    const pair = observe(store, "identity");
    const target = store.pointer.identity;
    const abs = path.isAbsolute(target) ? target : path.join(home, target);
    const text = fs.readFileSync(abs, "utf8");
    assert.equal(text.includes(`${pair.string}=${pair.integer}`), true);
    const parsed = parseLookBlock(look(store, "identity"));
    assert.equal(parsed.format, FORMAT_TEMPLATE);
  } finally {
    fs.rmSync(home, { recursive: true, force: true });
  }
});

test("memory io is the default", () => {
  const io = createMemoryIO();
  const store = mint({ io });
  assert.equal(store.io, io);
});

test("createHarness provides look observe verify wrap", () => {
  const h = createHarness();
  const lookBlock = h.look("identity");
  assert.equal(lookBlock.includes(FORMAT_TEMPLATE), true);
  const expected = h.formatExpected("identity");
  assert.equal(h.verify(expected, "identity").ok, true);

  const wrapFail = h.wrap(() => 42, "canary");
  assert.equal(wrapFail.ok, false);
  assert.equal(wrapFail.exitCode, 42);

  const wrapSuccess = h.wrap(() => 0, "canary");
  assert.equal(wrapSuccess.ok, true);
  assert.equal(wrapSuccess.look.includes("LOOK:"), true);
  const canaryExpected = h.formatExpected("canary");
  assert.equal(h.verify(canaryExpected, "canary").ok, true);
});

