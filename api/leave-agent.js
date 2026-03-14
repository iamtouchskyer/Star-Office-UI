import { getRedis, KEYS } from './_lib/redis.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { agentId, name } = req.body || {};

  const redis = getRedis();
  const agents = await redis.get(KEYS.AGENTS) || [];
  const idx = agents.findIndex(a =>
    (agentId && a.agentId === agentId) || (name && a.name === name)
  );
  if (idx === -1) return res.status(200).json({ ok: true }); // idempotent

  const agent = agents[idx];
  // Free join key
  if (agent.joinKey) {
    const keysData = await redis.get(KEYS.JOIN_KEYS) || { keys: [] };
    const keyObj = keysData.keys.find(k => k.key === agent.joinKey);
    if (keyObj && !keyObj.reusable) {
      keyObj.used = false;
      keyObj.usedBy = null;
      keyObj.usedByAgentId = null;
      await redis.set(KEYS.JOIN_KEYS, keysData);
    }
  }

  agents.splice(idx, 1);
  await redis.set(KEYS.AGENTS, agents);
  res.status(200).json({ ok: true });
}
