const motd = document.querySelector(".motd");

const icon = motd.querySelector(".favicon");
const name = motd.querySelector(".text .top .name");
const ping_icon = motd.querySelector(".text .top .ping .icon");
const ping_description = motd.querySelector(".text .top .ping .description");
const description = motd.querySelector(".text > .description");

const styles = {
    // Colors
    0: "color: #000000;",
    1: "color: #0000AA;",
    2: "color: #00AA00;",
    3: "color: #00AAAA;",
    4: "color: #AA0000;",
    5: "color: #AA00AA;",
    6: "color: #FFAA00;",
    7: "color: #AAAAAA;",
    8: "color: #555555;",
    9: "color: #5555FF;",
    a: "color: #55FF55;",
    b: "color: #55FFFF;",
    c: "color: #FF5555;",
    d: "color: #FF55FF;",
    e: "color: #FFFF55;",
    f: "color: #FFFFFF;",
    // Styles
    k: "// §k!",
    l: "font-weight: bold;",
    m: "text-decoration: strikethrough;",
    n: "text-decoration: underline;",
    o: "font-style: italic;",
};

function resolveMOTD(motd) {
    icon.setAttribute("src", motd.favicon);

    // ping_icon.classList.remove("pinging");
    // ping_icon.classList.add("online");

    ping_description.innerText = "■ Online";

    let d = "";

    if (typeof motd.description === "string") {
        d = motd.description;
    } else if (Array.isArray(motd.description)) {
        d = motd.description
            .map((obj) => obj["text"])
            .filter((v) => v != null)
            .join("");
    } else if (typeof motd.description === "object") {
        d = motd.description["text"];
    }

    description.innerHTML =
        d
            .replaceAll("\n", "<br />")
            .replace(
                /§([0-9a-z])/gi,
                (match, p1) =>
                    `<span style="${styles[p1.toLowerCase()] || ""}">`
            )
            .replace(/(§r)/gi, "</span>") + "</span>";
}

fetch(`/api/motd?host=${motdServer.host}&port=${motdServer.port}`)
    .then((response) => response.text())
    .then((text) => JSON.parse(text))
    .then((motd) => resolveMOTD(motd));
