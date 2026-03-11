module.exports = (req, res) => {
  res.status(200).json({
    state: process.env.STAR_OFFICE_STATUS || "idle",
    detail: process.env.STAR_OFFICE_MESSAGE || "AI助手办公室已上线！",
    timestamp: new Date().toISOString()
  });
}
