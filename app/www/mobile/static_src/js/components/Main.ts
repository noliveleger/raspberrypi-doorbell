import { Call } from "./Call";
import { Elements } from "./Elements";
import { Heartbeat } from "./Heartbeat";
import { IOptions, IStrings} from "./Interfaces";

declare const window: any;

class Main {

    private _heartbeat: Heartbeat = Heartbeat.getInstance();
    private _elements: Elements = Elements.getInstance();
    private _call!: Call;
    private _strings!: IStrings;

    public constructor(options: IOptions) {

        let self = this;

        if (location.protocol.indexOf('https') === 0) {
            self._strings = JSON.parse(options.strings);
            self._elements.message!.innerText = self._strings.beforeCall;

            self._call = new Call(options);
            self._bindEvents();
            self._rotateVideo(options);
            // self._heartbeat.start(options.heartbeat_interval);
            self._setContainerHeight();
        } else {
            alert('HTTPS must be enabled!');
        }
    }

    private _bindEvents(): void {

        let self = this,
            callButton = this._elements.callButton!,
            hangUpButton = this._elements.hangUpButton!,
            dial = this._elements.dial!;

        callButton.addEventListener('click', function() {
            dial.play();
            self._call.pickUp();
        });

        hangUpButton.addEventListener('click', function() {
            dial.pause();
            self._call.hangUp();
        });

        document.addEventListener('beforeunload', function() {
            self._heartbeat.stop();
            self._call.cleanUp();
        });

        window.addEventListener('onresize', function() {
            self._setContainerHeight();
        });

        window.addEventListener('orientationchange', function() {
            self._setContainerHeight();
        });
    }

    private _setContainerHeight() {

        let elements: Elements = Elements.getInstance();

        setTimeout(function() {
            window.scrollTop = 0;
            elements.container!.style.height = window.innerHeight + 'px';
        }, 200);
    }

    private _rotateVideo(options: IOptions) {
        let rotate = options.rotate;
        if (rotate !== 0) {
            this._elements.remoteVideo!.style.transform = `rotate(${rotate}deg)`;
        }
    }
}

window.Main = Main;
