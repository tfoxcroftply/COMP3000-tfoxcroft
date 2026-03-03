import test from "node:test";
import { createContext, useEffect, useState } from "react";


type ConnectionContextType = {
    connected: boolean,
    ip: string
}

export const ConnectionContext = createContext<ConnectionContextType>({
    connected: false,
    ip: "",
});

export function ConnectionHandler({children}: {children: React.ReactNode}) {
    const [connected, setConnected] = useState(false);
    const [disconnectedForLong, setDisconnectedForLong] = useState(false);
    const [appActive, setAppActive] = useState(false); // for checking first connect
    
    let ip: string = "unknown";
    let healthCheckingActive: boolean = false;

    const retrieveIp = async function() {
        // ignore
    };

    const delay = async function(milliseconds: number) {
        return new Promise(finish => setTimeout(finish, milliseconds));
    }

    const testConnection = async function() {
        try {
            const test = await fetch("http://127.0.0.1/api/health", { signal: AbortSignal.timeout(3000) })
            if (test.ok) {
                setConnected(true);
                return;
            }
        } catch {
            // ignore
        }

        setConnected(false);
    }

    useEffect(() => { // non refreshing
        const check = async function () {
            if (healthCheckingActive) { return; }
            healthCheckingActive = true

            while (true) {
                await testConnection();
                await delay(5000);
            }
        }
        
        check();
    },[])

    return (
        <ConnectionContext.Provider value={{connected, ip}}>
            {children}
        </ConnectionContext.Provider>
    )
}