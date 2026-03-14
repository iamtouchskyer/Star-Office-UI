export default function handler(req, res) {
  res.status(200).json({
    service: "star-office-ui",
    status: "ok",
    timestamp: new Date().toISOString()
  });
};