const BASE = '/api/v1'

async function handleResponse(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const parseBill = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return fetch(`${BASE}/bills/parse`, { method: 'POST', body: fd }).then(handleResponse)
}

export const getBill = (billId) =>
  fetch(`${BASE}/bills/${billId}`).then(handleResponse)

export const queryBill = (billId, question) =>
  fetch(`${BASE}/bills/${billId}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  }).then(handleResponse)

export const exportBill = (billId) =>
  fetch(`${BASE}/bills/${billId}/export`, { method: 'POST' }).then(handleResponse)

export const sendChat = (prompt, options = {}) =>
  fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      system_prompt: options.systemPrompt ?? null,
      temperature: options.temperature ?? 0.7,
      max_tokens: options.maxTokens ?? 512,
    }),
  }).then(handleResponse)
