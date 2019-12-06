export class Elements {

    protected static instance: Elements;
    public callButton: HTMLElement | null;
    public hangUpButton: HTMLElement | null;
    public playPauseButton: HTMLElement | null;
    public muteButton: HTMLElement | null;
    public fullscreenButton: HTMLElement | null;
    public remoteVideo: HTMLElement | null;
    public localVideo: HTMLElement | null;

    private constructor() {

        this.callButton = document.getElementById('btn-call');
        this.hangUpButton = document.getElementById('btn-hang-up');
        this.playPauseButton = document.getElementById('btn-pause');
        this.muteButton = document.getElementById('btn-mute');
        this.fullscreenButton = document.getElementById('btn-fullscreen');
        this.remoteVideo = document.getElementById('remote-video');
        this.localVideo = document.getElementById('local-video');

    }

    public static getInstance(): Elements {

        if (!Elements.instance) {
            Elements.instance = new Elements();
        }

        return Elements.instance;
    }

}
