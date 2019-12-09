export class Elements {

    protected static instance: Elements;
    public callButton: HTMLButtonElement | null;
    public container: HTMLDivElement | null;
    public dial: HTMLAudioElement | null;
    public hangUpButton: HTMLButtonElement | null;
    public localVideo: HTMLVideoElement | null;
    public message: HTMLDivElement | null;
    public overlay: HTMLDivElement | null;
    public remoteVideo: HTMLVideoElement | null;

    private constructor() {

        this.dial = <HTMLAudioElement> document.getElementById('dial');
        this.callButton = <HTMLButtonElement> document.getElementById('btn-call');
        this.container = <HTMLDivElement> document.getElementById('container');
        this.hangUpButton = <HTMLButtonElement> document.getElementById('btn-hang-up');
        this.localVideo = <HTMLVideoElement> document.getElementById('local-video');
        this.message = <HTMLDivElement> document.getElementById('message');
        this.overlay = <HTMLDivElement> document.getElementById('overlay');
        this.remoteVideo = <HTMLVideoElement> document.getElementById('remote-video');

    }

    public static getInstance(): Elements {

        if (!Elements.instance) {
            Elements.instance = new Elements();
        }

        return Elements.instance;
    }

}
