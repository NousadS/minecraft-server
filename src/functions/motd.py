import json
import socket
import struct
import typing

import pendulum


class VarInt:
    @staticmethod
    def pack(num: int) -> bytes:
        out = bytearray()

        while True:
            byte = num & 0x7F
            num >>= 7

            if num != 0:
                out.append(byte | 0x80)
            else:
                out.append(byte)
                break

        return bytes(out)

    @staticmethod
    def read(buffer: bytes, offset: int = 0):
        num = 0
        shift = 0
        bytes_read = 0

        while True:
            byte = buffer[offset + bytes_read]
            num |= (byte & 0x7F) << shift
            bytes_read += 1

            if (byte & 0x80) == 0:
                break

            shift += 7

        return {"value": num, "size": bytes_read}


class _MOTDCache:
    _cache: dict[str, typing.Any] = {}

    @classmethod
    def is_cached(cls, host: str, port: int) -> bool:
        return cls._cache.get(f"{host}:{port}", None) is not None and (
            pendulum.now() - cls._cache[f"{host}:{port}"]["last_sync"]
        ) < pendulum.Duration(minutes=5)

    @classmethod
    def get_cache(cls, host: str, port: int) -> dict[str, typing.Any]:
        tmp = (
            cls._cache[f"{host}:{port}"]["motd"].copy()
            if cls._cache.get(f"{host}:{port}", None) is not None
            else {}
        )

        if tmp.get("last_sync", None) is not None:
            del tmp["last_sync"]

        return tmp

    @classmethod
    def set_cache(cls, host: str, port: int, motd: dict[str, typing.Any]) -> None:
        cls._cache[f"{host}:{port}"] = {
            "last_sync": pendulum.now(),
            "motd": motd,
        }


class MOTD:
    def __init__(self, host: str, port: int = 25565) -> None:
        self.host: str = host
        self.port: int = port or 25565
        self.timeout: int = 5

        self.socket: socket.socket | None = None

    def open_socket(self, timeout: int = 5) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)

        self.socket.connect((self.host, self.port))

    def close_socket(self) -> None:
        if self.socket is None:
            raise ValueError("socket isn't open")

        self.socket.close()

    def send_handshake(self) -> None:
        if self.socket is None:
            raise ValueError("socket isn't open")

        host_bytes = self.host.encode("utf-8")

        # Handshake packet

        handshake = (
            b"\x00"  # packet id
            + VarInt.pack(47)  # protocol version
            + VarInt.pack(len(host_bytes))
            + host_bytes
            + struct.pack(">H", self.port)  # big-endian unsigned short
            + VarInt.pack(1)  # next state: status
        )

        self.socket.sendall(VarInt.pack(len(handshake)) + handshake)

    def send_request(self) -> None:
        if self.socket is None:
            raise ValueError("socket isn't open")

        # Request packet
        request = b"\x00"

        self.socket.sendall(VarInt.pack(len(request)) + request)

    def recv_response(self) -> dict[str, typing.Any | str | int] | None:
        if self.socket is None:
            raise ValueError("socket isn't open")

        # Read response

        data_buffer = b""

        while True:
            chunk = self.socket.recv(4096)

            if not chunk:
                break

            data_buffer += chunk

            offset = 0
            length_field = VarInt.read(data_buffer, offset)

            if len(data_buffer) < length_field["value"] + length_field["size"]:
                continue  # need more data

            offset += length_field["size"]

            packet_id = VarInt.read(data_buffer, offset)
            offset += packet_id["size"]

            if packet_id["value"] != 0:
                raise ValueError("invalid packet id")

            str_len = VarInt.read(data_buffer, offset)
            offset += str_len["size"]

            str_data = data_buffer[offset : offset + str_len["value"]].decode("utf-8")

            status = json.loads(str_data)

            motd: dict[str, typing.Any] = {
                "icon": status["favicon"].removeprefix("data:image/png;base64,"),
                "description": status["description"],
                "players": status["players"]["sample"],
                "online": status["players"]["online"],
            }

            _MOTDCache.set_cache(self.host, self.port, motd)

            return motd

    def get_motd(self) -> dict[str, typing.Any | str | int] | None:
        if _MOTDCache.is_cached(self.host, self.port):
            return _MOTDCache.get_cache(self.host, self.port)

        try:
            self.open_socket(self.timeout)

            self.send_handshake()
            self.send_request()

            return self.recv_response()
        except socket.timeout:
            raise TimeoutError("timeout")
        except Exception as e:
            raise ConnectionError(f"unknown (probably server doesn't exist): {e}")
        finally:
            self.close_socket()
