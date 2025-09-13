const express = require("express");
const router = express.Router();

// GET endpoint
router.get("/hello", (req, res) => {
  res.json({ message: "Hello from backend!" });
});

module.exports = router;
