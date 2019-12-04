(function() {

    'use strict';

    function App(options) {
        let call = null,
            elements = Elements.getInstance(),
            heartbeat;

        let init = function() {
            if (location.protocol === 'https:') {
                call = new Call(options);
                bindEvents();
                prepareVideo(options);
                heartbeat = new Heartbeat(options['heartbeat']);
                heartbeat.start();
            } else {
                alert('HTTPS must be enabled!');
            }
        };

        let bindEvents = function() {
            let callButton = elements.callButton,
                hangUpButton = elements.hangUpButton,
                btnPause = elements.playPauseButton,
                muteButton = elements.muteButton,
                fullscreenButton = elements.fullscreenButton;

            callButton.addEventListener('click', function() {
                call.pickUp();
            });
            // callButton.addEventListener('touchstart', start);
            hangUpButton.addEventListener('click', function() {
                call.hangUp();
            });
            // hangUpButton.addEventListener('touchstart', stop);

            btnPause.addEventListener('click', call.pause);
            muteButton.addEventListener('click', call.mute);
            fullscreenButton.addEventListener('click', call.fullscreen);

            document.addEventListener('beforeunload', call.cleanUp);
        };

        let prepareVideo = function() {
            let dimensions = options['resolution'].split('x'),
                width = dimensions[0],
                height = dimensions[1],
                rotate = options['rotate'];

            elements.remoteVideo.style.width = width + 'px';
            elements.remoteVideo.style.height = height + 'px';

            if (rotate !== 0) {
                elements.remoteVideo.style.transform = "rotate(" + rotate + "deg)";
            }
        };

        init();
    }

    /* Namespace declaration */
    window.App = App;

}());
