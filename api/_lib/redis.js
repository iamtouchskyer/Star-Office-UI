import { Redis } from '@upstash/redis';

let redis;

export function getRedis() {
  if (!redis) {
    redis = new Redis({
      url: process.env.KV_REST_API_URL,
      token: process.env.KV_REST_API_TOKEN,
    });
  }
  return redis;
}

// Redis key constants
export const KEYS = {
  STATE: 'office:state',
  AGENTS: 'office:agents',
  JOIN_KEYS: 'office:join_keys',
  MEMO: 'office:memo',
};

// Valid agent states
export const VALID_STATES = new Set(['idle', 'writing', 'researching', 'executing', 'syncing', 'error']);
export const WORKING_STATES = new Set(['writing', 'researching', 'executing']);

export const STATE_TO_AREA = {
  idle: 'breakroom',
  writing: 'writing',
  researching: 'writing',
  executing: 'writing',
  syncing: 'writing',
  error: 'error',
};

// Default state
export const DEFAULT_STATE = {
  state: 'idle',
  detail: 'AI助手办公室已上线！',
  progress: 0,
  updated_at: new Date().toISOString(),
  ttl_seconds: 300,
};

// Auto-idle check: if working state exceeds TTL, reset to idle
export function applyAutoIdle(stateObj) {
  if (!stateObj || !WORKING_STATES.has(stateObj.state)) return stateObj;
  const ttl = (stateObj.ttl_seconds || 300) * 1000;
  const age = Date.now() - new Date(stateObj.updated_at).getTime();
  if (age > ttl) {
    return { ...stateObj, state: 'idle', detail: '自动回到待命（超时）', updated_at: new Date().toISOString() };
  }
  return stateObj;
}
