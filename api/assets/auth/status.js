module.exports = function(req, res) {
  res.status(200).json({
    ok: true,
    authed: false
  });
}
