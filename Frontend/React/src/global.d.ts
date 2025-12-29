export {};

declare global {
    interface Window {
        electron: {
            discover: () => Promise<any>;
        }
    }
}

