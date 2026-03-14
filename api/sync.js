import { getRedis, KEYS, VALID_STATES, STATE_TO_AREA } from './_lib/redis.js';

/**
 * POST /api/sync
 * Bulk sync: receive full state snapshot from local backend, write to Redis.
 * Body: { password, state: {state, detail, ...}, agents: [...], memo?: {...} }
 */
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { password, state, agents, memo } = req.body || {};

  // Auth with ASSET_DRAWER_PASS
  if (password !== (process.env.ASSET_DRAWER_PASS || '1234')) {
    return res.status(403).json({ ok: false, error: 'Unauthorized' });
  }

  const redis = getRedis();
  const ops = [];

  // Sync main state
  if (state) {
    ops.push(redis.set(KEYS.STATE, {
      state: state.state || 'idle',
      detail: state.detail || '',
      progress: state.progress || 0,
      updated_at: state.updated_at || new Date().toISOString(),
      ttl_seconds: state.ttl_seconds || 300,
    }));
  }

  // Sync agents list
  if (agents) {
    const cleaned = agents.map(a => ({
      agentId: a.agentId || a.agent_id || 'unknown',
      name: a.name || 'unnamed',
      isMain: a.isMain || a.is_main || false,
      state: VALID_STATES.has(a.state) ? a.state : 'idle',
      detail: a.detail || '',
      updated_at: a.updated_at || new Date().toISOString(),
      area: STATE_TO_AREA[a.state] || a.area || 'breakroom',
      source: a.source || 'remote-openclaw',
      authStatus: a.authStatus || a.auth_status || 'approved',
      lastPushAt: a.lastPushAt || a.last_push_at || new Date().toISOString(),
      avatar: a.avatar || 'guest_role_1',
    }));
    ops.push(redis.set(KEYS.AGENTS, cleaned));
  }

  // Sync memo
  if (memo) {
    ops.push(redis.set(KEYS.MEMO, memo));
  }

  await Promise.all(ops);

  res.status(200).json({
    ok: true,
    synced: {
      state: !!state,
      agents: agents ? agents.length : 0,
      memo: !!memo,
    },
  });
}
