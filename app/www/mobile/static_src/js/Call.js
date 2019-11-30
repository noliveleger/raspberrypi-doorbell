/**
 * Based on UV4L Server WebRTC two-way Audio/Video/Data Intercom & Recorder webpage
 * The code not used for this project was removed.
 */
(function() {

    'use strict';

    function Call(options) {

        let elements = Elements.getInstance(),
            ws = null,
            peerConnection,
            dataChannel,
            localDataChannel,
            audioVideoStream,
            domainName,
            wsPort,
            wsEndpoint,
            peerConnectionConfig,
            peerConnectionOptions = { optional: [] },
            mediaConstraints = {
                optional: [],
                mandatory: {
                    OfferToReceiveAudio: true,
                    OfferToReceiveVideo: true
                }
            },
            remoteDesc = false,
            iceCandidates = [],
            RTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection,
            RTCSessionDescription = window.RTCSessionDescription,
            RTCIceCandidate = window.RTCIceCandidate;

        let init = function() {
            navigator.getUserMedia = navigator.mediaDevices.getUserMedia ||
                navigator.getUserMedia ||
                navigator.mozGetUserMedia ||
                navigator.webkitGetUserMedia ||
                navigator.msGetUserMedia;

            domainName = getValue('domainName');
            wsPort = getValue('wsPort');
            wsEndpoint = getValue('wsEndpoint');
            peerConnectionConfig = JSON.parse(getValue('iceServers'));
        };

        let getValue = function(value, defaultValue = null) {
            if (typeof(options[value]) !== 'undefined') {
                return options[value];
            } else {
                return defaultValue;
            }
        };

        let addIceCandidates = function() {
            iceCandidates.forEach(function (candidate) {
                peerConnection.addIceCandidate(candidate,
                    function() {
                        console.log("IceCandidate added: " + JSON.stringify(candidate));
                    },
                    function(error) {
                        console.error("addIceCandidate error: " + error);
                    }
                );
            });
            iceCandidates = [];
        };

        let createPeerConnection = function() {
            try {
                peerConnection = new RTCPeerConnection(peerConnectionConfig, peerConnectionOptions);
                peerConnection.onicecandidate = onIceCandidate;
                peerConnection.ontrack = onTrack;
                peerConnection.onremovestream = onRemoteStreamRemoved;
                console.log('Peer Connection successfully created!');
            } catch (e) {
                console.error('Create Peer Connection failed: ' + e);
            }
        };

        let onIceCandidate = function(event) {
            if (event.candidate) {
                let candidate = {
                    sdpMLineIndex: event.candidate.sdpMLineIndex,
                    sdpMid: event.candidate.sdpMid,
                    candidate: event.candidate.candidate
                };
                let request = {
                    what: "addIceCandidate",
                    data: JSON.stringify(candidate)
                };
                ws.send(JSON.stringify(request));
            } else {
                console.log("End of candidates.");
            }
        };

        let onRemoteStreamRemoved = function(event) {
            elements.remoteVideo.srcObject = null;
        };

        let onTrack = function(event) {
            console.log('Got remote track!');
            elements.remoteVideo.srcObject = event.streams[0];
        };

        this.cleanUp = function() {
            if (ws) {
                ws.onclose = function() {}; // disable onclose handler first
                this.hangUp();
            }
        };

        this.pickUp = function() {

            if ('WebSocket' in window) {
                elements.hangUpButton.disabled = false;
                elements.callButton.disabled = true;
                document.documentElement.style.cursor = 'wait';

                ws = new WebSocket('wss://' + domainName + ':' + wsPort + wsEndpoint);

                let call = function(stream) {
                    iceCandidates = [];
                    remoteDesc = false;
                    createPeerConnection();
                    if (stream) {
                        stream.getTracks().forEach(function(track) {
                            peerConnection.addTrack(track, stream);
                        });
                    }
                    let request = {
                        what: 'call',
                        options: {
                            force_hw_vcodec: getValue('webrtcForceHWVideoCodec'),
                            vformat: getValue('webrtcVideoFormat'),
                            trickle_ice: true
                        }
                    };
                    ws.send(JSON.stringify(request));
                    console.log("call(), request=" + JSON.stringify(request));
                };

                ws.onopen = function() {
                    audioVideoStream = null;

                    navigator.mediaDevices.getUserMedia({audio: true, video: false}).then(function(stream) {
                        console.log('Received local stream');
                        audioVideoStream = stream;
                        call(stream);
                        elements.localVideo.muted = true;
                        elements.localVideo.srcObject = stream;
                        // elements.localVideo.play();
                    }).catch(e => {
                        stop();
                        alert(`getUserMedia() error: ${e.name}`);
                    });
                };

                ws.onmessage = function(evt) {
                    let msg = JSON.parse(evt.data),
                        what = null,
                        data = null;

                    if (msg.what !== 'undefined') {
                        what = msg.what;
                        data = msg.data;
                    }

                    switch (what) {

                        case 'offer':
                            peerConnection.setRemoteDescription(new RTCSessionDescription(JSON.parse(data)))
                                .then(() => {
                                    remoteDesc = true;
                                    addIceCandidates();
                                    peerConnection.createAnswer(mediaConstraints).then(sessionDescription => {
                                        peerConnection.setLocalDescription(sessionDescription).then();
                                        let request = {
                                            what: 'answer',
                                            data: JSON.stringify(sessionDescription)
                                        };
                                        ws.send(JSON.stringify(request));
                                    }).catch(error => {
                                        alert('Failed to createAnswer: ' + error);
                                    });
                                }).catch(event => {
                                    alert('Failed to set remote description (unsupported codec on this browser?): ' + event);
                                    stop();
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
                            let elt = JSON.parse(msg.data);
                            let candidate = new RTCIceCandidate({sdpMLineIndex: elt.sdpMLineIndex, candidate: elt.candidate});
                            iceCandidates.push(candidate);
                            if (remoteDesc)
                                addIceCandidates();
                            document.documentElement.style.cursor = 'default';
                            break;

                        case 'iceCandidates': // when trickle ice is not enabled
                            let candidates = JSON.parse(msg.data);
                            for (let i = 0; candidates && i < candidates.length; i++) {
                                let elt = candidates[i];
                                let candidate = new RTCIceCandidate({sdpMLineIndex: elt.sdpMLineIndex, candidate: elt.candidate});
                                iceCandidates.push(candidate);
                            }
                            if (remoteDesc) {
                                addIceCandidates();
                            }
                            document.documentElement.style.cursor = 'default';
                            break;
                    }
                };

                ws.onclose = function(evt) {
                    if (peerConnection) {
                        peerConnection.close();
                        peerConnection = null;
                    }
                    document.getElementById("btn-hang-up").disabled = true;
                    document.getElementById("btn-call").disabled = false;
                    document.documentElement.style.cursor = 'default';
                };

                ws.onerror = function (evt) {
                    alert("An error has occurred!");
                    ws.close();
                };

            } else {
                alert("Sorry, this browser does not support WebSockets.");
            }
        };

        this.hangUp = function() {
            if (dataChannel) {
                console.log("closing data channels");
                dataChannel.close();
                dataChannel = null;
                document.getElementById('dataChannels').disabled = true;
            }
            if (localDataChannel) {
                console.log("closing local data channels");
                localDataChannel.close();
                localDataChannel = null;
            }
            if (audioVideoStream) {
                try {
                    if (audioVideoStream.getVideoTracks().length)
                        audioVideoStream.getVideoTracks()[0].stop();
                    if (audioVideoStream.getAudioTracks().length)
                        audioVideoStream.getAudioTracks()[0].stop();
                    audioVideoStream.stop(); // deprecated
                } catch (e) {
                    for (let i = 0; i < audioVideoStream.getTracks().length; i++)
                        audioVideoStream.getTracks()[i].stop();
                }
                audioVideoStream = null;
            }

            elements.remoteVideo.srcObject = null;
            elements.localVideo.srcObject = null;

            if (peerConnection) {
                peerConnection.close();
                peerConnection = null;
            }
            if (ws) {
                ws.close();
                ws = null;
            }
            elements.hangUpButton.disabled = true;
            elements.callButton.disabled = false;

            document.documentElement.style.cursor = 'default';
        };

        this.mute = function() {
            elements.remoteVideo.muted = !elements.remoteVideo.muted;
        };

        this.pause = function() {
            if (elements.remoteVideo.paused) {
                elements.remoteVideo.play();
            } else {
                elements.remoteVideo.pause();
            }
        };

        this.fullscreen = function() {
            if (elements.remoteVideo.requestFullScreen) {
                elements.remoteVideo.requestFullScreen();
            } else if (elements.remoteVideo.webkitRequestFullScreen) {
                elements.remoteVideo.webkitRequestFullScreen();
            } else if (elements.remoteVideo.mozRequestFullScreen) {
                elements.remoteVideo.mozRequestFullScreen();
            }
        };

        init();
    }

    /* Namespace declaration */
    window.Call = Call;

}());
