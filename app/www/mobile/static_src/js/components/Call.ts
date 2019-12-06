/**
 * Based on UV4L Server WebRTC two-way Audio/Video/Data Intercom & Recorder webpage
 * The code not used for this project was removed.
 */
import { Elements } from "./Elements";
import { IOptions } from "./Main";
import { Requests } from "./Requests";

export class Call {

    private _elements: Elements = Elements.getInstance();
    private _ws: any = null;
    private _peerConnection: any;
    private _options: IOptions;
    private _dataChannel: any;
    private _localDataChannel: any;
    private _audioVideoStream: any;
    private _domainName: string;
    private _wsPort: number;
    private _wsEndpoint: string;
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

    public constructor(options: IOptions) {

        let self = this;

        navigator.getUserMedia = navigator.mediaDevices.getUserMedia ||
            navigator.getUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.msGetUserMedia;

        self._domainName = options.domainName;
        self._wsPort = options.wsPort;
        self._wsEndpoint = options.wsEndpoint;
        self._peerConnectionConfig = JSON.parse(options.iceServers);
        self._options = options;

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
                console.log('End of candidates');
            }
        };

        let onRemoteStreamRemoved = function(event: any) {
            self._elements.remoteVideo.srcObject = null;
        };

        let onTrack = function(event: any) {
            self._elements.remoteVideo.srcObject = event.streams[0];
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
            self.hangUp(force=true);
        }
    }

    public pickUp() {

        let self = this;

        Requests.requestJSON({'url': '/validate-session'}).then(() => {

            self._elements.callButton.classList.add('disabled');
            self._elements.hangUpButton.classList.remove('disabled');

            if ('WebSocket' in window) {

                self._elements.hangUpButton.disabled = false;
                self._elements.callButton.disabled = true;
                document.documentElement.style.cursor = 'wait';

                self._ws = new WebSocket('wss://' + self._domainName + ':' + self._wsPort + self._wsEndpoint);

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
                        self._elements.localVideo.muted = true;
                        self._elements.localVideo.srcObject = stream;
                        // elements.localVideo.play();
                    }).catch(e => {
                        console.log('ERROR ' + e);
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
                                    }).catch((event: error) => {
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
                            document.documentElement.style.cursor = 'default';
                            break;

                        case 'iceCandidates': // when trickle ice is not enabled
                            let candidates = JSON.parse(msg.data);
                            for (let i = 0; candidates && i < candidates.length; i++) {
                                let elt = candidates[i],
                                    candidate = new self._RTCIceCandidate({sdpMLineIndex: elt.sdpMLineIndex, candidate: elt.candidate});
                                self._iceCandidates.push(candidate);
                            }
                            if (self._remoteDesc) { self._addIceCandidates(); }
                            document.documentElement.style.cursor = 'default';
                            break;
                    }
                };

                self._ws.onclose = function(evt: any) {
                    console.log('On close')
                    if (self._peerConnection) {
                        console.log('PerrConnection.close()');
                        self._peerConnection.close();
                        self._peerConnection = null;
                    }
                };

                self._ws.onerror = function (evt:any) {
                    self.cleanUp();
                    alert("An error has occurred!");
                };

            } else {
                alert("Sorry, this browser does not support WebSockets.");
            }
        }).catch((response) => {
            console.log(response);
            console.log('REJECTED');
            self.cleanUp();
        });
    }

    public hangUp(force: boolean = false) {

        this._elements.hangUpButton.classList.add('disabled');
        this._elements.hangUpButton.disabled = true;

        if (this._dataChannel) {
            console.log("closing data channels");
            this._dataChannel.close();
            this._dataChannel = null;
            document.getElementById('dataChannels').disabled = true;
        }

        if (this._localDataChannel) {
            console.log("closing local data channels");
            this._localDataChannel.close();
            this._localDataChannel = null;
        }

        if (this._audioVideoStream) {
            try {
                if (this._audioVideoStream.getVideoTracks().length)
                    this._audioVideoStream.getVideoTracks()[0].stop();
                if (this._audioVideoStream.getAudioTracks().length)
                    this._audioVideoStream.getAudioTracks()[0].stop();
                // this._audioVideoStream.stop(); // deprecated
            } catch (e) {
                for (let i = 0; i < this._audioVideoStream.getTracks().length; i++)
                    this._audioVideoStream.getTracks()[i].stop();
            }
            this._audioVideoStream = null;
        }

        this._elements.remoteVideo.srcObject = null;
        this._elements.localVideo.srcObject = null;

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

    public mute() {
        let elements: Elements = Elements.getInstance();
        elements.remoteVideo.muted = !elements.remoteVideo.muted;
    }

    public pause() {
        let elements: Elements = Elements.getInstance();
        if (elements.remoteVideo.paused) {
            elements.remoteVideo.play();
        } else {
            elements.remoteVideo.pause();
        }
    }

    public fullscreen() {
        let elements: Elements = Elements.getInstance();
        if (elements.remoteVideo.requestFullScreen) {
            elements.remoteVideo.requestFullScreen();
        } else if (elements.remoteVideo.webkitRequestFullScreen) {
            elements.remoteVideo.webkitRequestFullScreen();
        } else if (elements.remoteVideo.mozRequestFullScreen) {
            elements.remoteVideo.mozRequestFullScreen();
        }
    }
}


