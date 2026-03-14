import { getRedis, KEYS } from './_lib/redis.js';

export default async function handler(req, res) {
  const redis = getRedis();

  if (req.method === 'POST') {
    const { date, memo, content } = req.body || {};
    const data = { date: date || new Date().toISOString().slice(0, 10), memo: memo || '', content: content || [] };
    await redis.set(KEYS.MEMO, data);
    return res.status(200).json({ ok: true, ...data });
  }

  // GET
  const memo = await redis.get(KEYS.MEMO);
  if (memo) return res.status(200).json(memo);
  res.status(200).json({ date: '', content: [], has_content: false });
}
