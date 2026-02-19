import { GAME_CONFIG } from "$lib/config";

export class Logger {
    private source: string;

    constructor(source: string) {
        this.source = source;
    }

    private formatArgs(...args: any[]): any[] {
        return [`[${this.source}]`, ...args];
    }

    log(...args: any[]) {
        if (!GAME_CONFIG.development.devMode) return;
        console.log(...this.formatArgs(...args));
    }

    warn(...args: any[]) {
        if (!GAME_CONFIG.development.devMode) return;
        console.warn(...this.formatArgs(...args));
    }

    error(...args: any[]) {
        if (!GAME_CONFIG.development.devMode) return;
        console.error(...this.formatArgs(...args));
    }

    info(...args: any[]) {
        if (!GAME_CONFIG.development.devMode) return;
        console.info(...this.formatArgs(...args));
    }
}
