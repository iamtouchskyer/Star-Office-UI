module.exports = function(req, res) {
  res.status(200).json({
    success: true,
    date: "",
    memo: "暂无昨日日记"
  });
}
