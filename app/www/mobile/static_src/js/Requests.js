(function() {

    'use strict';

    function Requests() {}

    /**
     * Public static function (request of Requests)
     * @return {Promise}
     * @author http://ccoenraets.github.io/es6-tutorial-data/promisify/
     */

    Requests.request = (function() {
        return function(obj) {
            return new Promise((resolve, reject) => {
                let xhr = new XMLHttpRequest();
                xhr.open(obj.method || 'GET', obj.url);
                if (obj.headers) {
                    Object.keys(obj.headers).forEach(key => {
                        xhr.setRequestHeader(key, obj.headers[key]);
                    });
                }
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(xhr.response);
                    } else {
                        reject(xhr.statusText);
                    }
                };
                xhr.onerror = () => reject(xhr.statusText);
                xhr.send(obj.body);
            });
        };
    })();

    /* Namespace declaration */
    window.Requests = Requests;

}());
