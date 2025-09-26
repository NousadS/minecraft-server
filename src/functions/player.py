import base64
import json
import typing
from io import BytesIO

import pendulum
import requests
from PIL import Image


class _PlayerCache:
    _cache: dict[str, typing.Any] = {}

    @classmethod
    def is_cached(cls, uuid: str = "", name: str = "") -> bool:
        if cls._cache.get(uuid, None) is not None and (
            pendulum.now() - cls._cache[uuid]["last_sync"]
        ) < pendulum.Duration(minutes=5):
            return cls._cache[uuid]

        if cls._cache.get(name, None) is not None and (
            pendulum.now() - cls._cache[name]["last_sync"]
        ) < pendulum.Duration(minutes=5):
            return cls._cache[name]

        return False

    @classmethod
    def get_cache(cls, uuid: str = "", name: str = "") -> dict[str, typing.Any]:
        assert uuid != "" or name != ""

        if cls._cache.get(uuid, None) is not None:
            tmp = cls._cache[uuid].copy()
            del tmp["last_sync"]

            return tmp

        if cls._cache.get(name, None) is not None:
            tmp = cls._cache[name].copy()
            del tmp["last_sync"]

            return tmp

        return {}

    @classmethod
    def set_cache(
        cls, profile: dict[str, typing.Any], uuid: str = "", name: str = ""
    ) -> None:
        assert uuid != "" or name != ""

        if uuid != "":
            cls._cache[uuid] = profile.copy()
            cls._cache[uuid]["last_sync"] = pendulum.now()

        if name != "":
            cls._cache[name] = profile.copy()
            cls._cache[name]["last_sync"] = pendulum.now()


class Player:
    def __init__(self, uuid: str | list[str] = "", name: str | list[str] = "") -> None:
        if isinstance(uuid, str):
            self.uuids: list[str] = [uuid]
        else:
            self.uuids: list[str] = uuid

        if isinstance(name, str):
            self.names: list[str] = [name]
        else:
            self.names: list[str] = name

        self.uuids = list(filter(lambda s: s is not None and s != "", self.uuids))
        self.names = list(filter(lambda s: s is not None and s != "", self.names))

        assert len(self.uuids) > 0 or len(self.names) > 0

        self.profiles: list[dict[str, str]] = []

    def resolve_profile(self, uuid: str = "", name: str = "") -> dict[str, str]:
        assert uuid != "" or name != ""

        if _PlayerCache.is_cached(uuid=uuid, name=name):
            return _PlayerCache.get_cache(uuid=uuid, name=name)
        
        if uuid == "":
            response: requests.Response = requests.get(
                f"https://api.minecraftservices.com/minecraft/profile/lookup/name/{name.removeprefix('.')}"
            )

            try:
                data = response.json()

                uuid = data["id"]
            except (json.JSONDecodeError, KeyError):
                uuid = "00000000000000000000000000000000"

        response: requests.Response = requests.get(
            f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}?unsigned=true"
        )

        try:
            data: dict[str, typing.Any] = response.json()
            profile: dict[str, typing.Any] = json.loads(
                base64.b64decode(data["properties"][0]["value"])
            )
            skin_url: str = profile["textures"]["SKIN"]["url"]

            skin_response: requests.Response = requests.get(skin_url)
            skin: Image = Image.open(BytesIO(skin_response.content))  # type: ignore
            head: Image = skin.crop((8, 8, 16, 16))  # type: ignore

            buf: BytesIO = BytesIO()

            head.save(buf, format="PNG")  # type: ignore

            head_b64: str = base64.b64encode(buf.getvalue()).decode("utf-8")

            t: dict[str, str] = {
                "uuid": data["id"],
                "name": name.removeprefix(".") or data["name"] or uuid,
                "head": head_b64,
                "type": "Bedrock" if name.startswith(".") else "Java",
            }

            _PlayerCache.set_cache(uuid=uuid, name=name, profile=t)

            return t
        except (json.JSONDecodeError, KeyError):
            t: dict[str, str] = {
                "uuid": uuid,
                "name": name,
                "head": "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAA7UlEQVR4nDXBvy8DUQDA8e979+6HJ6qD9EQ0lfgD/ANmkVjthg4Gf4JYTMRmoIN0FouhBpbGn2AykFTRlA6XS5rjcr337pl8PmJjbcGZCpSQFNZgjEVKia88nANlKgAwrmI+ClgMBBaPJCuwzqIAzg72CP2AuahG/jMFT5J+jzm5vUfcHO07HQb8FgWeF5JOU1pxg/fhCwBShwE7h+dcP64TlTNacYPLu5j2RY/a0griqr3l4uVVVFin1+8DsLu9yejjlcEkQWal5XM04LTboak1Ta057nRJshyBj3r7mlBVDoCH5yf+ZbmlKGf8Abs0WXs4UrwAAAAAAElFTkSuQmCC",
                "type": "Bedrock" if name.startswith(".") else "Java",
            }

            _PlayerCache.set_cache(uuid=uuid, name=name, profile=t)

            return t

    def get_profiles(
        self,
    ) -> dict[str, typing.Any | str | int] | list[dict[str, typing.Any | str | int]]:
        self.profiles = []

        names: list[str] = []

        if len(self.uuids) > 0:
            for uuid in self.uuids:
                profile: dict[str, str] = self.resolve_profile(uuid=uuid)

                names.append(profile["name"])

                self.profiles.append(profile)

        if len(self.names) > 0:
            for name in self.names:
                if name not in names:
                    self.profiles.append(self.resolve_profile(name=name))

        self.profiles = list(filter(lambda e: e["name"] != "", self.profiles))

        return self.profiles if len(self.profiles) > 1 else self.profiles[0]
