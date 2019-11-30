(function() {

    'use strict';

    function App(options) {
        let call = null,
            elements = Elements.getInstance();

        let init = function() {
            if (location.protocol === 'https:') {
                call = new Call(options);
                bindEvents();
                prepareVideo(options);
            } else {
                alert('HTTPS must be enabled!');
            }
        };

        let getValue = function(value, defaultValue = null) {
            if (typeof(options[value]) !== 'undefined') {
                return options[value];
            } else {
                return defaultValue;
            }
        };

        let bindEvents = function() {
            let callButton = elements.callButton,
                hangUpButton = elements.hangUpButton,
                btnPause = elements.playPauseButton,
                muteButton = elements.muteButton,
                fullscreenButton = elements.fullscreenButton;

            callButton.addEventListener('click', function() {
                 callButton.classList.add('disabled');
                 hangUpButton.classList.remove('disabled');
                call.pickUp();
            });
            // callButton.addEventListener('touchstart', start);
            hangUpButton.addEventListener('click', function() {
                call.hangUp();
                callButton.classList.remove('disabled');
                hangUpButton.classList.add('disabled');
            });
            // hangUpButton.addEventListener('touchstart', stop);

            btnPause.addEventListener('click', call.pause);
            muteButton.addEventListener('click', call.mute);
            fullscreenButton.addEventListener('click', call.fullscreen);

            document.addEventListener('beforeunload', call.cleanUp);
        };

        let prepareVideo = function() {
            let dimensions = getValue('resolution', '640x480').split('x'),
                width = dimensions[0],
                height = dimensions[1],
                rotate = getValue('rotate');

            document.getElementById('remote-video').style.width = width + 'px';
            document.getElementById('remote-video').style.height = height + 'px';

            if (rotate !== 0) {
                document.getElementById("remote-video").style.transform = "rotate(" + rotate + "deg)";
            }
        };

        init();
    }

    /* Namespace declaration */
    window.App = App;

}());
