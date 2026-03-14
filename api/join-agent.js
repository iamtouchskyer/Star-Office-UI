import { getRedis, KEYS, VALID_STATES, STATE_TO_AREA } from './_lib/redis.js';

const AVATARS = ['guest_role_1', 'guest_role_2', 'guest_role_3', 'guest_role_4', 'guest_role_5', 'guest_role_6'];

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { name, state, detail, joinKey } = req.body || {};
  if (!name || !joinKey) {
    return res.status(400).json({ ok: false, error: 'name and joinKey required' });
  }

  const redis = getRedis();

  // Validate join key
  const keysData = await redis.get(KEYS.JOIN_KEYS) || { keys: [] };
  const keyObj = keysData.keys.find(k => k.key === joinKey);
  if (!keyObj) {
    return res.status(403).json({ ok: false, error: 'Invalid join key' });
  }
  if (keyObj.expiresAt && new Date(keyObj.expiresAt) < new Date()) {
    return res.status(403).json({ ok: false, error: 'Join key expired' });
  }

  // Generate agent ID
  const agentId = `agent_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
  const agentState = (state && VALID_STATES.has(state)) ? state : 'idle';

  const agent = {
    agentId,
    name,
    isMain: false,
    state: agentState,
    detail: detail || '刚加入办公室',
    updated_at: new Date().toISOString(),
    area: STATE_TO_AREA[agentState] || 'breakroom',
    source: 'remote-openclaw',
    joinKey,
    authStatus: 'approved', // auto-approve with valid key
    authApprovedAt: new Date().toISOString(),
    authExpiresAt: null,
    authRejectedAt: null,
    lastPushAt: new Date().toISOString(),
    avatar: AVATARS[Math.floor(Math.random() * AVATARS.length)],
  };

  // Mark key as used
  keyObj.used = true;
  keyObj.usedBy = name;
  keyObj.usedByAgentId = agentId;
  keyObj.usedAt = new Date().toISOString();
  await redis.set(KEYS.JOIN_KEYS, keysData);

  // Add agent to list
  const agents = await redis.get(KEYS.AGENTS) || [];
  agents.push(agent);
  await redis.set(KEYS.AGENTS, agents);

  res.status(200).json({
    ok: true,
    agentId,
    authStatus: 'approved',
    nextStep: 'Use /agent-push to send status updates',
  });
}
