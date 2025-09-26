const express = require("express");
const router = express.Router();

const getMOTD = require("../api/motd.cjs");

router.get("/motd", async (req, res) => {
    const { host, port = 25565 } = req.query;

    if (!host) {
        res.status(400).json({ error: "Missing `host`" });

        return;
    }

    try {
        const motd = await getMOTD(host, port);

        res.json(motd);
    } catch (e) {
        res.status(500).json({ error: String(e) });
    }
});

module.exports = router;
