import { getRedis, KEYS, VALID_STATES } from './_lib/redis.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { state, detail } = req.body || {};
  const redis = getRedis();
  const current = await redis.get(KEYS.STATE) || {};

  const updated = {
    state: (state && VALID_STATES.has(state)) ? state : (current.state || 'idle'),
    detail: detail || current.detail || '',
    progress: 0,
    updated_at: new Date().toISOString(),
    ttl_seconds: current.ttl_seconds || 300,
  };

  await redis.set(KEYS.STATE, updated);
  res.status(200).json({ status: 'ok', ...updated });
}
