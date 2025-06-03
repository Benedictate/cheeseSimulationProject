const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

app.post("/run-simulation", async (req, res) => {
    try {
        const response = await axios.post("http://127.0.0.1:5000/simulate", req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3001, () => console.log("Node.js server running on port 3001"));
