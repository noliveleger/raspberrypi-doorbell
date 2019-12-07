import { Call } from "./Call";
import { Elements } from "./Elements";
import { Heartbeat } from "./Heartbeat";

export interface IOptions {
    domainName: string;
    wsPort: number;
    wsEndpoint: string;
    iceServers: string;
    webrtcVideoFormat: string;
    webrtcForceHWVideoCodec: number,
    rotate: string,
    heartbeat_interval: number
}

declare const window: any;

class Main {

    private _heartbeat: Heartbeat = Heartbeat.getInstance();
    private _elements: Elements = Elements.getInstance();
    private _call!: Call;

    public constructor(options: IOptions) {

        if (location.protocol.indexOf('https') === 0) {
            this._call = new Call(options);
            this._bindEvents();
            // prepareVideo(options);
            this._heartbeat.start(options.heartbeat_interval);
        } else {
            alert('HTTPS must be enabled!');
        }

    }

    private _bindEvents(): void {

        let self = this,
            callButton = this._elements.callButton!,
            hangUpButton = this._elements.hangUpButton!,
            btnPause = this._elements.playPauseButton!,
            muteButton = this._elements.muteButton!,
            fullscreenButton = this._elements.fullscreenButton!;

        callButton.addEventListener('click', function() {
            self._call.pickUp();
        });
        // callButton.addEventListener('touchstart', start);
        hangUpButton.addEventListener('click', function() {
            self._call.hangUp();
        });

        btnPause.addEventListener('click', self._call.pause);
        muteButton.addEventListener('click', self._call.mute);
        fullscreenButton.addEventListener('click', self._call.fullscreen);

        document.addEventListener('beforeunload', function() {
            self._heartbeat.stop();
            self._call.cleanUp();
        });
    }
}

window.Main = Main;
