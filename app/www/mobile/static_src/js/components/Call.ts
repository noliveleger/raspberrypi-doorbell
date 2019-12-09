/**
 * Based on UV4L Server WebRTC two-way Audio/Video/Data Intercom & Recorder webpage
 * The code not used for this project was removed.
 */
import { Elements } from "./Elements";
import {IOptions, IStrings} from "./Interfaces";
import { Requests } from "./Requests";

export class Call {

    private _elements: Elements = Elements.getInstance();
    private _ws: any = null;
    private _peerConnection: any;
    private _options!: IOptions;
    private _dataChannel: any;
    private _localDataChannel: any;
    private _audioVideoStream: any;
    private _peerConnectionConfig: any;
    private _peerConnectionOptions: any = { optional: [] };
    private _mediaConstraints: any = {
        optional: [],
            mandatory: {
            OfferToReceiveAudio: true,
            OfferToReceiveVideo: true
        }
    };
    private _remoteDesc: boolean = false;
    private _iceCandidates: any[] = [];

    private _RTCPeerConnection: any = window.RTCPeerConnection || window.webkitRTCPeerConnection;
    private _RTCSessionDescription: any = window.RTCSessionDescription;
    private _RTCIceCandidate: any = window.RTCIceCandidate;
    private _strings!: IStrings;

    public constructor(options: IOptions) {

        let self = this;

        navigator.getUserMedia = navigator.mediaDevices.getUserMedia ||
            navigator.getUserMedia;
        self._peerConnectionConfig = JSON.parse(options.iceServers);
        self._options = options;
        self._strings = JSON.parse(self._options.strings);
    }

    private _addIceCandidates() {

        let self = this;

        self._iceCandidates.forEach(function(candidate: any) {
            self._peerConnection.addIceCandidate(candidate).then(() => {
                console.log("IceCandidate added: " + JSON.stringify(candidate));
            }).catch((error: any) => {
                console.error("addIceCandidate error: " + error);
            });
        });

        self._iceCandidates = [];

    }

    private _createPeerConnection() {

        let self = this;

        let onIceCandidate = function(event: any) {
            if (event.candidate) {
                let candidate = {
                    sdpMLineIndex: event.candidate.sdpMLineIndex,
                    sdpMid: event.candidate.sdpMid,
                    candidate: event.candidate.candidate
                };
                let request = {
                    what: 'addIceCandidate',
                    data: JSON.stringify(candidate)
                };
                self._ws.send(JSON.stringify(request));
            } else {
                self._elements.remoteVideo!.play();
                console.log('End of candidates');
            }
        };

        let onRemoteStreamRemoved = function(event: any) {
            self._elements.remoteVideo!.srcObject = null;
        };

        let onTrack = function(event: any) {
            self._elements.remoteVideo!.srcObject = event.streams[0];
        };

        try {
            self._peerConnection = new self._RTCPeerConnection(self._peerConnectionConfig, self._peerConnectionOptions);
            self._peerConnection.onicecandidate = onIceCandidate;
            self._peerConnection.ontrack = onTrack;
            self._peerConnection.onremovestream = onRemoteStreamRemoved;
            console.log('Peer Connection successfully created!');
        } catch (e) {
            console.error('Create Peer Connection failed: ' + e);
        }

    }

    public cleanUp() {

        let self = this;

        if (self._ws) {
            self._ws.onclose = function() {}; // disable onclose handler first
            self.hangUp(true);
        }
    }

    public pickUp() {

        let self = this;

        Requests.requestJSON({'url': '/validate-session'}).then(() => {

            self._elements.callButton!.classList.add('hide');
            self._elements.hangUpButton!.classList.remove('hide');
            self._elements.message!.innerText = self._strings.onProgressCall;

            if ('WebSocket' in window) {

                self._ws = new WebSocket('wss://'
                    + self._options.domainName + ':' + self._options.wsPort
                    + self._options.wsEndpoint);

                let call = function(stream: any) {
                    self._iceCandidates = [];
                    self._remoteDesc = false;
                    self._createPeerConnection();
                    if (stream) {
                        stream.getTracks().forEach(function(track: any) {
                            self._peerConnection.addTrack(track, stream);
                        });
                    }
                    let request = {
                        what: 'call',
                        options: {
                            force_hw_vcodec: self._options.webrtcForceHWVideoCodec,
                            vformat: self._options.webrtcVideoFormat,
                            trickle_ice: true
                        }
                    };
                    self._ws.send(JSON.stringify(request));
                    console.log("call(), request=" + JSON.stringify(request));
                };

                self._ws.onopen = function() {
                    self._audioVideoStream = null;

                    navigator.mediaDevices.getUserMedia({audio: true, video: false}).then(function(stream) {
                        console.log('Received local stream');
                        self._audioVideoStream = stream;
                        call(stream);
                        self._elements.localVideo!.muted = true;
                        self._elements.localVideo!.srcObject = stream;
                    }).catch(e => {
                        self.cleanUp();
                        alert(`getUserMedia() error: ${e.name}`);
                    });
                };

                self._ws.onmessage = function(evt: any) {
                    let msg = JSON.parse(evt.data),
                        what: any = null,
                        data: any = null;

                    if (msg.what !== 'undefined') {
                        what = msg.what;
                        data = msg.data;
                    }

                    switch (what) {

                        case 'offer':
                            Requests.requestJSON({'url': '/pick-up'}).then(() => {

                                self._elements.dial!.pause();
                                self._elements.container!.classList.add('on-call');

                                self._peerConnection.setRemoteDescription(new self._RTCSessionDescription(JSON.parse(data)))
                                    .then(() => {
                                        self._remoteDesc = true;
                                        self._addIceCandidates();
                                        self._peerConnection.createAnswer(self._mediaConstraints).then((sessionDescription: any) => {
                                            self._peerConnection.setLocalDescription(sessionDescription).then();
                                            let request = {
                                                what: 'answer',
                                                data: JSON.stringify(sessionDescription)
                                            };
                                            self._ws.send(JSON.stringify(request));
                                        }).catch((error: any) => {
                                            alert('Failed to createAnswer: ' + error);
                                        });
                                    }).catch((event: any) => {
                                    alert('Failed to set remote description (unsupported codec on this browser?): ' + event);
                                    self.cleanUp();
                                });
                            });
                            break;

                        case 'answer':
                            break;

                        case 'message':
                            alert(msg.data);
                            break;

                        case 'iceCandidate': // when trickle is enabled
                            if (!msg.data) {
                                console.log('Ice Gathering Complete');
                                break;
                            }
                            let elt = JSON.parse(msg.data),
                                candidate = new self._RTCIceCandidate({sdpMLineIndex: elt.sdpMLineIndex, candidate: elt.candidate});
                            self._iceCandidates.push(candidate);
                            if (self._remoteDesc) { self._addIceCandidates(); }
                            break;

                        case 'iceCandidates': // when trickle ice is not enabled
                            let candidates = JSON.parse(msg.data);
                            for (let i = 0; candidates && i < candidates.length; i++) {
                                let elt = candidates[i],
                                    candidate = new self._RTCIceCandidate({sdpMLineIndex: elt.sdpMLineIndex, candidate: elt.candidate});
                                self._iceCandidates.push(candidate);
                            }
                            if (self._remoteDesc) { self._addIceCandidates(); }
                            break;
                    }
                };

                self._ws.onclose = function(evt: any) {
                    if (self._peerConnection) {
                        console.log('PeerConnection.close()');
                        self._peerConnection.close();
                        self._peerConnection = null;
                    }
                };

                self._ws.onerror = function (evt: any) {
                    self.cleanUp();
                    alert("An error has occurred!");
                };

            } else {
                alert("Sorry, this browser does not support WebSockets.");
            }
        }).catch((response) => {
            self.cleanUp();
        });
    }

    public hangUp(force: boolean = false) {

        let self = this;

        self._elements.hangUpButton!.classList.add('hide');
        self._elements.message!.innerText = this._strings.terminatedCall;
        self._elements.container!.classList.remove('on-call');

        if (this._dataChannel) {
            this._dataChannel.close();
            this._dataChannel = null;
        }

        if (this._localDataChannel) {
            this._localDataChannel.close();
            this._localDataChannel = null;
        }

        if (this._audioVideoStream) {
            try {
                if (this._audioVideoStream.getVideoTracks().length)
                    this._audioVideoStream.getVideoTracks()[0].stop();
                if (this._audioVideoStream.getAudioTracks().length)
                    this._audioVideoStream.getAudioTracks()[0].stop();
            } catch (e) {
                for (let i = 0; i < this._audioVideoStream.getTracks().length; i++)
                    this._audioVideoStream.getTracks()[i].stop();
            }
            this._audioVideoStream = null;
        }

        this._elements.remoteVideo!.srcObject = null;
        this._elements.localVideo!.srcObject = null;

        if (this._peerConnection) {
            this._peerConnection.close();
            this._peerConnection = null;
        }

        if (this._ws) {
            this._ws.close();
            this._ws = null;
        }

        if (!force) {
            Requests.requestJSON({'url': '/hang-up'});
        }
    }

}


