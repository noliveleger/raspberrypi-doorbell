(function() {

    'use strict';

    function Heartbeat() {

        let self = this,
            timer;

        let init = function() {};

        self.start = function() {
            Requests.request({'url': '/heartbeat'})
                .then(response => {
                    timer = setTimeout( () => self.start(), 20 * 1000);
                })
                .catch(response => {
                    // Session or call is not valid anymore
                    console.log('Heartbeat missed :-(');
                    self.stop();
                });
        };

        init();

        self.stop = function() {
            clearTimeout(timer);
            timer = null;
        }
    }

    /* Namespace declaration */
    window.Heartbeat = Heartbeat;

}());
