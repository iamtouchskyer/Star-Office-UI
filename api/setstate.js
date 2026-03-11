module.exports = (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }
  
  res.status(200).json({
    status: req.body?.status || "idle",
    message: req.body?.message || "",
    timestamp: new Date().toISOString()
  });
}