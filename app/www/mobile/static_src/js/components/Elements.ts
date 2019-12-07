export class Elements {

    protected static instance: Elements;
    public callButton: HTMLButtonElement | null;
    public hangUpButton: HTMLButtonElement | null;
    public playPauseButton: HTMLButtonElement | null;
    public muteButton: HTMLButtonElement | null;
    public fullscreenButton: HTMLButtonElement | null;
    public remoteVideo: HTMLVideoElement | null;
    public localVideo: HTMLVideoElement | null;

    private constructor() {

        this.callButton = <HTMLButtonElement> document.getElementById('btn-call')!;
        this.hangUpButton = <HTMLButtonElement> document.getElementById('btn-hang-up');
        this.playPauseButton = <HTMLButtonElement> document.getElementById('btn-pause');
        this.muteButton = <HTMLButtonElement> document.getElementById('btn-mute');
        this.fullscreenButton = <HTMLButtonElement> document.getElementById('btn-fullscreen');
        this.remoteVideo = <HTMLVideoElement> document.getElementById('remote-video');
        this.localVideo = <HTMLVideoElement> document.getElementById('local-video');

    }

    public static getInstance(): Elements {

        if (!Elements.instance) {
            Elements.instance = new Elements();
        }

        return Elements.instance;
    }

}
