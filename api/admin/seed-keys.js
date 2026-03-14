import { getRedis, KEYS } from '../_lib/redis.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  // Simple auth - use ASSET_DRAWER_PASS env var
  const { password } = req.body || {};
  if (password !== (process.env.ASSET_DRAWER_PASS || '1234')) {
    return res.status(403).json({ ok: false, error: 'Unauthorized' });
  }

  const redis = getRedis();
  const existing = await redis.get(KEYS.JOIN_KEYS);
  if (existing && existing.keys && existing.keys.length > 0) {
    return res.status(200).json({ ok: true, msg: 'Keys already exist', count: existing.keys.length });
  }

  // Seed default join keys
  const keysData = {
    keys: [
      { key: 'ocj_starteam01', used: false, reusable: true, maxConcurrent: 3 },
      { key: 'ocj_starteam02', used: false, reusable: true, maxConcurrent: 3 },
      { key: 'ocj_starteam03', used: false, reusable: false, maxConcurrent: 1 },
    ]
  };
  await redis.set(KEYS.JOIN_KEYS, keysData);
  res.status(200).json({ ok: true, msg: 'Keys seeded', count: keysData.keys.length });
}
