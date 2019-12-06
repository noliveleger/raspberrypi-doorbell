import { Requests } from "./Requests";

export class Heartbeat {

    private _timer: any;
    private static instance: Heartbeat;

    private constructor() {}

    public static getInstance(): Heartbeat {

        if (!Heartbeat.instance) {
            Heartbeat.instance = new Heartbeat();
        }

        return Heartbeat.instance;
    }

    public start(interval: number) {
        let self = this;

        Requests.request({'url': '/heartbeat'})
            .then((response: any) => {
                this._timer = setTimeout( () => self.start(interval), interval * 1000);
            })
            .catch((response: any) => {
                // Session or call is not valid anymore
                console.log('Heartbeat missed :-(');
                self.stop();
                location.reload();
            });
    }

    public stop() {
        clearTimeout(this._timer);
        this._timer = null;
    }

}
