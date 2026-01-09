const express = require("express");
const axios = require("axios");
const router = express.Router();

// ML Service URL (Python Flask)
const ML_SERVICE_URL = "http://localhost:5003";

router.post("/", async (req, res) => {
  try {
    const { question = "" } = req.body || {};

    // Proxy query to Python ML Service
    const response = await axios.post(`${ML_SERVICE_URL}/api/nlq`, {
      question
    });

    // Return the response directly
    return res.json(response.data);

  } catch (error) {
    console.error("[nlq] Proxy error:", error.message);

    // Fallback if ML service is down
    return res.status(500).json({
      error: "Failed to process query via ML Agent. Service might be unavailable.",
      details: error.message
    });
  }
});

module.exports = router;
