const net = require("net");

function packVarInt(num) {
    let out = [];

    while (true) {
        let byte = num & 0x7f;
        num >>>= 7;
        if (num !== 0) {
            out.push(byte | 0x80);
        } else {
            out.push(byte);
            break;
        }
    }

    return Buffer.from(out);
}

function readVarInt(buffer, offset = 0) {
    let num = 0,
        shift = 0,
        bytesRead = 0;

    while (true) {
        let byte = buffer[offset + bytesRead];
        num |= (byte & 0x7f) << shift;
        bytesRead++;
        if ((byte & 0x80) === 0) break;
        shift += 7;
    }

    return { value: num, size: bytesRead };
}

function getMOTD(host, port = 25565) {
    return new Promise((resolve, reject) => {
        const socket = new net.Socket();

        // Timeout

        socket.setTimeout(5000);

        socket.on("timeout", () => {
            socket.destroy();
            reject("timeout");
        });

        // Error

        socket.on("error", () => {
            socket.destroy();

            reject("unknown (probably server doesn't exist)");
        });

        // Resolving data

        let dataBuffer = Buffer.alloc(0);

        socket.on("data", (chunk) => {
            dataBuffer = Buffer.concat([dataBuffer, chunk]);

            try {
                let offset = 0;
                let lengthField = readVarInt(dataBuffer, offset);

                if (dataBuffer.length < lengthField.value + lengthField.size)
                    return; // wait more

                offset += lengthField.size;

                let packetId = readVarInt(dataBuffer, offset);

                offset += packetId.size;

                if (packetId.value !== 0) throw new Error("Invalid packet id");

                let strLen = readVarInt(dataBuffer, offset);

                offset += strLen.size;

                let strData = dataBuffer
                    .slice(offset, offset + strLen.value)
                    .toString("utf8");

                socket.end();

                let status = JSON.parse(strData);

                resolve(status);
            } catch (err) {
                // ignore until we have full packet
            }
        });

        // Connection

        socket.connect(port, host, () => {
            const hostBuf = Buffer.from(host, "utf8");

            // Handshake packet
            const handshake = Buffer.concat([
                Buffer.from([0x00]), // packet id
                packVarInt(47), // protocol version
                packVarInt(hostBuf.length),
                hostBuf,
                Buffer.from([(port >> 8) & 0xff, port & 0xff]),
                packVarInt(1), // next state: status
            ]);

            socket.write(
                Buffer.concat([packVarInt(handshake.length), handshake])
            );

            // Request packet
            const request = Buffer.from([0x00]);

            socket.write(Buffer.concat([packVarInt(request.length), request]));
        });
    });
}

module.exports = getMOTD;
