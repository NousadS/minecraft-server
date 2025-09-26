// Imports

const express = require("express");
const ejs = require("ejs");
const path = require("path");

const getMOTD = require("../api/motd.cjs");

// Router definition

const router = express.Router();

// Routes

// Index route

router.get("/", async (req, res) => {
    res.render("index")
});

router.get("/motd", async (req, res) => {
    res.render("motd", {
        host: req.query.host || "server8ahvgg.aternos.me",
        port: req.query.port || 37358
    })
});

module.exports = router;
