import { getRedis, KEYS } from './_lib/redis.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { agentId } = req.body || {};
  if (!agentId) return res.status(400).json({ ok: false, error: 'agentId required' });

  const redis = getRedis();
  const agents = await redis.get(KEYS.AGENTS) || [];
  const agent = agents.find(a => a.agentId === agentId);
  if (!agent) return res.status(404).json({ ok: false, error: 'Agent not found' });

  agent.authStatus = 'approved';
  agent.authApprovedAt = new Date().toISOString();
  await redis.set(KEYS.AGENTS, agents);

  res.status(200).json({ ok: true, agentId, authStatus: 'approved' });
}
