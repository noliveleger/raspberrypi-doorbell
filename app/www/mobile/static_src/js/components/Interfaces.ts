export interface IOptions {
    domainName: string;
    wsPort: number;
    wsEndpoint: string;
    iceServers: string;
    webrtcVideoFormat: string;
    webrtcForceHWVideoCodec: number,
    rotate: number,
    heartbeat_interval: number,
    strings: string
}

export interface IStrings {
    beforeCall: string,
    onProgressCall: string,
    terminatedCall: string
}

