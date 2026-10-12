// Clean pasted Anthropic keys and turn API errors into plain English.

export function normalizeApiKey(raw) {
  let key = String(raw || "").trim();
  key = key.replace(/^['"]|['"]$/g, "");
  const embedded = key.match(/sk-ant-api[a-zA-Z0-9_-]+/);
  if (embedded) return embedded[0];
  if (/api[_-]?key\s*[:=]/i.test(key)) key = key.replace(/^.*[:=]\s*/, "").trim();
  key = key.replace(/\s+/g, "");
  return key;
}

export function validateApiKeyShape(key) {
  if (!key) return "";
  if (key.startsWith("sk-proj-") || (key.startsWith("sk-") && !key.startsWith("sk-ant"))) {
    return "That looks like an OpenAI key. This app needs an Anthropic key from console.anthropic.com. It should start with sk-ant-.";
  }
  if (!key.startsWith("sk-ant")) {
    return "Anthropic keys start with sk-ant-. Copy the whole key from the Create Key popup.";
  }
  if (key.length < 50) {
    return "That key looks too short. Anthropic only shows the full key once. Make a new key and copy it right away.";
  }
  return "";
}

export function keyHint(key) {
  const clean = normalizeApiKey(key);
  if (!clean || clean.length < 8) return "";
  return "Ends in " + clean.slice(-4);
}

export function explainApiFailure(status, message) {
  const text = String(message || "").toLowerCase();
  if (status === 401 || (text.includes("invalid") && (text.includes("api") || text.includes("x-api-key")))) {
    return (
      "Anthropic rejected this key on this browser. " +
      "Make a new key at console.anthropic.com (starts with sk-ant-). " +
      "Paste it here and tap Save settings. " +
      "Safari on your phone and Chrome on your computer each need their own paste."
    );
  }
  if (text.includes("credit") || text.includes("balance") || text.includes("billing") || text.includes("purchase")) {
    return "Your Anthropic API balance is too low. Add credits at console.anthropic.com, then tap Retry lookup.";
  }
  return message || "Lookup failed";
}
