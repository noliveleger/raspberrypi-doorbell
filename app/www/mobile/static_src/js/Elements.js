/**
 * Element.js
 * Tiny helper to retrieve DOM elements without calling
 * `document.getElementById()` all the time
 */
(function() {

    'use strict';

    //singleton instance
    let instance = null;

    function Elements() {

        //singleton
        if (!instance) instance = this;
        else return instance;

        //private
        let self = this;

        self.initialize = function() {
            self.callButton = document.getElementById('btn-call');
            self.hangUpButton = document.getElementById('btn-hang-up');
            self.playPauseButton = document.getElementById('btn-pause');
            self.muteButton = document.getElementById('btn-mute');
            self.fullscreenButton = document.getElementById('btn-fullscreen');
            self.remoteVideo = document.getElementById('remote-video');
            self.localVideo = document.getElementById('local-video');
        };

        // constructor
        self.initialize.apply(self, arguments);
        return self;
    }


    /**
     * Public static function (getInstance of Elements)
     * @return {Elements} instance
     */
    Elements.getInstance = (function() {
        return function() {
            if (!instance) return new Elements();
            else return instance;
        };
    })();

    /* Namespace declaration */
    window.Elements = Elements;

}());
