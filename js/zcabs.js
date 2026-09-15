// SPDX-License-Identifier: AGPL-3.0-or-later
// zcabs protocol. Memory store by default. Inject io for files.

export const FORMAT_TEMPLATE = "the {string} number is {integer}";
export const INT_MIN = 100000;
export const INT_MAX = 999999;
export const DECOY_COUNT = 16;

const DECOY_STEMS = [
  "apple", "orange", "grape", "mango", "peach", "cherry", "lemon",
  "cedar", "maple", "river", "quartz", "ember", "nickel", "cobalt",
  "harbor", "ridge", "pollen", "willow", "flint", "amber",
  "sienna", "copper", "basalt", "nimbus",
];

const SPOKEN = /\bthe\s+([A-Za-z][A-Za-z0-9_\-]*)\s+number\s+is\s+(\d+)\b/gi;
const PAIR_LINE = /^([A-Za-z][A-Za-z0-9_\-]*)\s*=\s*(\d+)\s*$/;
const KEY_EQ = /\b([A-Za-z][A-Za-z0-9_\-]*)\s*=\s*(\d{6})\b/g;
const VALUE = /\bZCABS_VALUE\s*[:=]\s*(\d+)\b/gi;

export function isLiveInteger(n) {
  return Number.isInteger(n) && n >= INT_MIN && n <= INT_MAX;
}

export function formatSpoken(string, integer) {
  return `the ${string} number is ${integer}`;
}

export function emitLook(target) {
  return `LOOK: ${target || "unavailable"}\nFORMAT: ${FORMAT_TEMPLATE}`;
}

export function parsePair(text) {
  for (const raw of String(text).split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const m = PAIR_LINE.exec(line);
    PAIR_LINE.lastIndex = 0;
    if (!m) continue;
    const n = Number(m[2]);
    if (!isLiveInteger(n)) continue;
    return { string: m[1], integer: n };
  }
  return null;
}

export function parseLookBlock(text) {
  const look = /LOOK:\s*(.*)/.exec(text);
  const fmt = /FORMAT:\s*(.*)/.exec(text);
  return {
    look: look ? look[1].trim() : null,
    format: fmt ? fmt[1].trim() : null,
  };
}

function hexBytes(n) {
  const out = [];
  if (typeof crypto !== "undefined" && crypto.getRandomValues) {
    const buf = new Uint8Array(n);
    crypto.getRandomValues(buf);
    for (const b of buf) out.push(b.toString(16).padStart(2, "0"));
    return out.join("");
  }
  for (let i = 0; i < n; i++) {
    out.push(Math.floor(Math.random() * 256).toString(16).padStart(2, "0"));
  }
  return out.join("");
}

function randomInt(used) {
  for (let i = 0; i < 10000; i++) {
    let n;
    if (typeof crypto !== "undefined" && crypto.getRandomValues) {
      const buf = new Uint32Array(1);
      crypto.getRandomValues(buf);
      n = INT_MIN + (buf[0] % (INT_MAX - INT_MIN + 1));
    } else {
      n = INT_MIN + Math.floor(Math.random() * (INT_MAX - INT_MIN + 1));
    }
    if (!used.has(n)) {
      used.add(n);
      return n;
    }
  }
  throw new Error("ERROR: failed to allocate a unique integer");
}

function token(name) {
  const s = String(name || "").trim().toLowerCase();
  if (!s || !/^[a-z][a-z0-9_\-]*$/.test(s)) {
    throw new Error("ERROR: invalid key");
  }
  return s;
}

export function createMemoryIO() {
  const files = new Map();
  return {
    files,
    write(p, t) {
      files.set(p, t);
    },
    read(p) {
      if (!files.has(p)) throw new Error("ERROR: LOOK file missing");
      return files.get(p);
    },
    exists(p) {
      return files.has(p);
    },
    join(...parts) {
      return parts.join("/");
    },
  };
}

export function mint(opts = {}) {
  const identityKey = token(opts.identity || "banana");
  const extra = (opts.caps || []).map(token);
  const caps = ["canary", ...extra].filter((k, i, a) => k !== identityKey && k !== "identity" && a.indexOf(k) === i);
  const decoyN = Math.max(DECOY_COUNT, opts.decoys || DECOY_COUNT);
  const io = opts.io || createMemoryIO();
  const used = new Set();
  const usedKeys = new Set([identityKey, ...caps]);
  const pointer = {};
  const bucket = "store";

  const identPath = io.join(bucket, `f_${hexBytes(6)}.dat`);
  io.write(identPath, `${identityKey}=${randomInt(used)}\n`);
  pointer.identity = identPath;

  for (const name of caps) {
    const p = io.join(bucket, `f_${hexBytes(6)}.dat`);
    io.write(p, `${name}=${randomInt(used)}\n`);
    pointer[name] = p;
  }

  const stems = DECOY_STEMS.filter((s) => !usedKeys.has(s));
  for (let i = 0; i < decoyN; i++) {
    const dKey = i < stems.length ? stems[i] : `d_${hexBytes(4)}`;
    const p = io.join(bucket, `f_${hexBytes(6)}.dat`);
    io.write(p, `${dKey}=${randomInt(used)}\n`);
  }

  return { io, pointer, identityKey, caps, decoys: decoyN };
}

export function look(store, key = "identity") {
  const k = String(key).trim().toLowerCase();
  const target = store.pointer[k];
  if (!target) throw new Error("ERROR: unknown key");
  return emitLook(target);
}

export function observe(store, key) {
  const k = String(key).trim().toLowerCase();
  const target = store.pointer[k];
  if (!target) throw new Error("ERROR: unknown key");
  const pair = parsePair(store.io.read(target));
  if (!pair) throw new Error("ERROR: LOOK file empty");
  return pair;
}

export function rotate(store, key) {
  const k = String(key).trim().toLowerCase();
  const target = store.pointer[k];
  if (!target) throw new Error("ERROR: unknown key");
  const pair = parsePair(store.io.read(target));
  if (!pair) throw new Error("ERROR: LOOK file empty");
  const used = allIntegers(store);
  used.delete(pair.integer);
  const n = randomInt(used);
  store.io.write(target, `${pair.string}=${n}\n`);
}

export function allIntegers(store) {
  const used = new Set();
  for (const [p, text] of store.io.files.entries()) {
    if (!String(p).includes("f_") || !String(p).endsWith(".dat")) continue;
    const pair = parsePair(text);
    if (pair) used.add(pair.integer);
  }
  return used;
}

export function verify(store, text, key) {
  if (!text || !String(text).trim()) {
    return { ok: false, reason: "ERROR: empty candidate" };
  }
  let pair;
  try {
    pair = observe(store, key);
  } catch (e) {
    return { ok: false, reason: String(e.message || e) };
  }
  const spoken = extractSpoken(String(text), pair.string);
  if (!spoken.length) {
    return { ok: false, reason: "ERROR: invariant failed. no structured retrieval in candidate." };
  }
  for (const item of spoken) {
    if (item.string.toLowerCase() === pair.string.toLowerCase() && item.integer === pair.integer) {
      return { ok: true, reason: "PASS", extracted: item.integer };
    }
  }
  return { ok: false, reason: "ERROR: invariant failed. candidate does not match store." };
}

export function extractSpoken(text, expectedString) {
  const found = [];
  const seen = new Set();
  function add(string, integer, form) {
    if (!isLiveInteger(integer)) return;
    const id = `${string.toLowerCase()}|${integer}|${form}`;
    if (seen.has(id)) return;
    seen.add(id);
    found.push({ string, integer, form });
  }
  for (const m of text.matchAll(SPOKEN)) add(m[1], Number(m[2]), "format");
  for (const m of text.matchAll(KEY_EQ)) add(m[1], Number(m[2]), "pair");
  if (expectedString) {
    for (const m of text.matchAll(VALUE)) add(expectedString, Number(m[1]), "zcabs_value");
    const want = expectedString.toLowerCase();
    const preferred = found.filter((s) => s.string.toLowerCase() === want);
    if (preferred.length) return preferred;
  }
  return found;
}

export function createFsIO(fs, pathMod, home) {
  const files = new Map();
  return {
    files,
    write(p, t) {
      const abs = pathMod.isAbsolute(p) ? p : pathMod.join(home, p);
      fs.mkdirSync(pathMod.dirname(abs), { recursive: true });
      fs.writeFileSync(abs, t, "utf8");
      try {
        fs.chmodSync(abs, 0o600);
      } catch {
        /* windows */
      }
      files.set(p, t);
    },
    read(p) {
      const abs = pathMod.isAbsolute(p) ? p : pathMod.join(home, p);
      return fs.readFileSync(abs, "utf8");
    },
    exists(p) {
      const abs = pathMod.isAbsolute(p) ? p : pathMod.join(home, p);
      return fs.existsSync(abs);
    },
    join: (...parts) => pathMod.join(...parts),
  };
}
