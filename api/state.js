import { getRedis, KEYS, DEFAULT_STATE, applyAutoIdle } from './_lib/redis.js';

export default async function handler(req, res) {
  const redis = getRedis();
  let state = await redis.get(KEYS.STATE);
  if (!state) state = DEFAULT_STATE;
  state = applyAutoIdle(state);
  res.status(200).json(state);
}
