// Vercel Serverless API endpoints

const mockState = {
  status: process.env.STAR_OFFICE_STATUS || "idle",
  message: process.env.STAR_OFFICE_MESSAGE || "AI助手办公室已上线！",
  timestamp: new Date().toISOString()
};

const mockMemo = {
  date: "2026-03-09",
  content: [
    "• AI助手办公室成功部署到Vercel",
    "• 支持多Agent协作展示", 
    "• 通过环境变量配置默认状态"
  ],
  has_content: true
};

module.exports = (req, res) => {
  const { url, method } = req;
  
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  // Health check
  if (url === '/api/health' || url === '/health') {
    res.status(200).json({
      service: "star-office-ui",
      status: "ok", 
      timestamp: new Date().toISOString()
    });
    return;
  }
  
  // Get state
  if (url === '/api/state' || url === '/state') {
    res.status(200).json(mockState);
    return;
  }
  
  // Get agents
  if (url === '/api/agents' || url === '/agents') {
    res.status(200).json({
      agents: [],
      count: 0
    });
    return;
  }
  
  // Get memo
  if (url === '/api/memo' || url === '/memo' || url === '/api/yesterday-memo' || url === '/yesterday-memo') {
    res.status(200).json(mockMemo);
    return;
  }
  
  // Set state
  if ((url === '/api/set_state' || url === '/set_state') && method === 'POST') {
    const newState = {
      status: req.body?.status || "idle",
      message: req.body?.message || "",
      timestamp: new Date().toISOString()
    };
    res.status(200).json(newState);
    return;
  }
  
  // Default 404
  res.status(404).json({ error: "Not found", path: url });
};