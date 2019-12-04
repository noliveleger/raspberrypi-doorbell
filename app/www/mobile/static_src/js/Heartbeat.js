(function() {

    'use strict';

    //singleton instance
    let instance = null;

    function Heartbeat(interval) {

        //singleton
        if (!instance) instance = this;
        else return instance;


        let self = this,
            timer;

        let init = function() {};

        self.start = function() {
            Requests.request({'url': '/heartbeat'})
                .then(response => {
                    timer = setTimeout( () => self.start(), interval * 1000);
                })
                .catch(response => {
                    // Session or call is not valid anymore
                    console.log('Heartbeat missed :-(');
                    self.stop();
                    location.reload();
                });
        };

        init();

        self.stop = function() {
            clearTimeout(timer);
            timer = null;
        }
    }

    /**
     * Public static function (getInstance of Heartbeat)
     * @return {Heartbeat} instance
     */
    Heartbeat.getInstance = (function() {
        return function() {
            if (!instance) return new Heartbeat();
            else return instance;
        };
    })();

    /* Namespace declaration */
    window.Heartbeat = Heartbeat;

}());
