import { getRedis, KEYS } from './_lib/redis.js';

const STALE_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

export default async function handler(req, res) {
  const redis = getRedis();
  let agents = await redis.get(KEYS.AGENTS) || [];

  // Auto-cleanup stale agents (no push in 5 min → offline)
  const now = Date.now();
  let changed = false;
  for (const agent of agents) {
    if (agent.authStatus === 'approved' && agent.lastPushAt) {
      const age = now - new Date(agent.lastPushAt).getTime();
      if (age > STALE_TIMEOUT_MS) {
        agent.authStatus = 'offline';
        changed = true;
      }
    }
  }
  // Remove offline agents
  const active = agents.filter(a => a.authStatus !== 'offline');
  if (active.length !== agents.length) changed = true;
  if (changed) await redis.set(KEYS.AGENTS, active);

  res.status(200).json(active);
}
