import { getRedis, KEYS, VALID_STATES, STATE_TO_AREA } from './_lib/redis.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { agentId, joinKey, state, detail, name } = req.body || {};
  if (!agentId || !joinKey) {
    return res.status(400).json({ ok: false, error: 'agentId and joinKey required' });
  }

  const redis = getRedis();
  const agents = await redis.get(KEYS.AGENTS) || [];
  const agent = agents.find(a => a.agentId === agentId);

  if (!agent) {
    return res.status(404).json({ ok: false, error: 'Agent not found. Call /join-agent first.' });
  }

  if (agent.joinKey !== joinKey) {
    return res.status(403).json({ ok: false, error: 'Invalid joinKey for this agent' });
  }

  // Update agent state
  const newState = (state && VALID_STATES.has(state)) ? state : agent.state;
  agent.state = newState;
  agent.detail = detail || agent.detail;
  agent.area = STATE_TO_AREA[newState] || 'breakroom';
  agent.updated_at = new Date().toISOString();
  agent.lastPushAt = new Date().toISOString();
  if (name) agent.name = name;

  await redis.set(KEYS.AGENTS, agents);

  // Also update main state if this looks like the main agent push
  // (convention: agentId contains "main" or is the only agent)
  if (agentId.includes('main') || agent.isMain) {
    await redis.set(KEYS.STATE, {
      state: newState,
      detail: detail || agent.detail,
      progress: 0,
      updated_at: new Date().toISOString(),
      ttl_seconds: 300,
    });
  }

  res.status(200).json({ ok: true, agentId, area: agent.area });
}
