const online_status = `<i class="icon nf nf-fa-circle"></i> Online`;
const offline_status = `<i class="icon nf nf-cod-circle"></i> Offline`;

const online_attribute = [`data-status`, `online`];
const offline_attribute = [`data-status`, `offline`];

const default_head = `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAA7UlEQVR4nDXBvy8DUQDA8e979+6HJ6qD9EQ0lfgD/ANmkVjthg4Gf4JYTMRmoIN0FouhBpbGn2AykFTRlA6XS5rjcr337pl8PmJjbcGZCpSQFNZgjEVKia88nANlKgAwrmI+ClgMBBaPJCuwzqIAzg72CP2AuahG/jMFT5J+jzm5vUfcHO07HQb8FgWeF5JOU1pxg/fhCwBShwE7h+dcP64TlTNacYPLu5j2RY/a0griqr3l4uVVVFin1+8DsLu9yejjlcEkQWal5XM04LTboak1Ta057nRJshyBj3r7mlBVDoCH5yf+ZbmlKGf8Abs0WXs4UrwAAAAAAElFTkSuQmCC`;

const java_tag = `
    <div class="tag green">
        <img class="icon" src="/static/images/icons/minecraft.png" /> Java
    </div>
`;
const bedrock_tag = `
    <div class="tag gray">
        <img class="icon" src="/static/images/icons/bedrock.png" /> Bedrock
    </div>
`;

const host = `server8ahvgg.aternos.me`;
const port = `37358`;

const container = document.querySelector(".player-list");
const player_template = document.querySelector("#player-template");

function loadPlayer(element, i) {
    const clone = player_template.content.cloneNode(true);

    const player = clone.querySelector(".player");
    const player_head = player.querySelector(".head");
    const player_name = player.querySelector(".name");
    const player_status = player.querySelector(".status");
    const player_button_to_buildings = player.querySelector(".button.to-buildings");

    player.setAttribute("data-uuid", element.uuid);
    player.style.animationDelay = `${i * 0.2}s`;

    player_head.setAttribute("src", `data:image/png;base64,${element.head}`);
    player_head.setAttribute("title", element.uuid);

    player_name.innerHTML = `${element.name} ${element.type == "Java" ? java_tag : bedrock_tag}`;

    player_button_to_buildings.setAttribute("href", `/sites?player=${element.name}`)

    setPlayerOnline(player);

    container.appendChild(clone);
}

function setPlayerOnline(element) {
    const player = element;
    const player_head = player.querySelector(".head");
    const player_name = player.querySelector(".name");
    const player_status = player.querySelector(".status");

    player_head.setAttribute(...online_attribute);
    player_name.setAttribute(...online_attribute);

    player_status.style.opacity = "0";

    setTimeout(() => {
        player_status.setAttribute(...online_attribute);
        player_status.innerHTML = `${online_status}`;
        player_status.style.opacity = "1";
    }, 1000);
}

function setPlayerOffline(element) {
    const player = element;
    const player_head = player.querySelector(".head");
    const player_name = player.querySelector(".name");
    const player_status = player.querySelector(".status");

    player_head.setAttribute(...offline_attribute);
    player_name.setAttribute(...offline_attribute);

    player_status.style.opacity = "0";

    setTimeout(() => {
        player_status.setAttribute(...offline_attribute);
        player_status.innerHTML = `${offline_status}`;
        player_status.style.opacity = "1";
    }, 1000);
}

function reloadPlayers() {
    fetch(`api/players_at_server?host=${host}&port=${port}`)
        .then((response) => response.text())
        .then((text) => JSON.parse(text))
        .then((data) => {
            data.sort((a, b) => {
                if (a.type == "Java") {
                    if (b.type == "Bedrock") return -1;
                    
                    return [a.name, b.name].sort()[0] == a.name ? 1 : -1;
                } else {
                    if (b.type == "Java") return 1;
                    
                    return [a.name, b.name].sort()[0] == a.name ? 1 : -1;
                }
            });

            if (
                container.hasAttribute("data-loaded") &&
                container.getAttribute("data-loaded") == "true"
            ) {
                let DOM_uuids = Array.from(container.children).map((e) =>
                    e.getAttribute("data-uuid")
                );
                let data_uuids = data.map((e) => e.uuid);

                Array.from(container.children).forEach((element) => {
                    if (
                        !data_uuids.includes(element.getAttribute("data-uuid"))
                    ) {
                        setPlayerOffline(element);
                    }
                });

                Array.from(container.children).forEach((element) => {
                    if (
                        data_uuids.includes(element.getAttribute("data-uuid"))
                    ) {
                        setPlayerOnline(element);
                    }
                });

                data.forEach((element, i) => {
                    if (!DOM_uuids.includes(element.uuid))
                        loadPlayer(element, i);
                });
            } else {
                container.innerHTML = ``;

                data.forEach(loadPlayer);

                container.setAttribute("data-loaded", true);
            }
        })
        .catch((reason) => {})
        .finally(() => {
            setTimeout(reloadPlayers, 50000);
        });
}

window.addEventListener("load", (event) => {
    setTimeout(reloadPlayers, 100);
});
