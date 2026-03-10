export default function handler(req, res) {
  res.status(200).json({
    status: process.env.STAR_OFFICE_STATUS || "idle",
    message: process.env.STAR_OFFICE_MESSAGE || "AI助手办公室已上线！",
    timestamp: new Date().toISOString()
  });
}