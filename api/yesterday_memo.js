import { getRedis, KEYS } from './_lib/redis.js';

export default async function handler(req, res) {
  const redis = getRedis();
  const memo = await redis.get(KEYS.MEMO);
  if (memo) {
    return res.status(200).json({ success: true, ...memo });
  }
  res.status(200).json({ success: true, date: '', memo: '暂无昨日日记' });
}
