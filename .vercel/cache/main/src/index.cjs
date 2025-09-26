// Imports

const express = require("express");
const ejs = require("ejs");
const path = require("path");

const staticRouter = express.static(path.join(__dirname, "static"));
const apiRouter = require("./routers/api.cjs");
const pagesRouter = require("./routers/pages.cjs");

// App definition

const app = express();

// View engine EJS

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "pages"));

// Routers

app.use("/static", staticRouter);
app.use("/api", apiRouter);
app.use("/", pagesRouter);

// Fallback Routers

app.use((req, res) => {
    res.status(404).send("Not Found");
});

app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).send("Internal Server Error");
});

module.exports = app;
