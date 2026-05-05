import { createContext, useContext, useEffect, useState, useRef } from "react";

import { delay } from "../components/Utils"

type ConnectionContextType = {
    connected: boolean,
    started: boolean,
    devMode: boolean,
    ip: string,
    startConnection: () => void,
    getPath: (path: string) => string;
}

export const ConnectionContext = createContext<ConnectionContextType>({
    connected: false,
    started: false,
    devMode: false,
    ip: "Unknown",
    startConnection: () => null,
    getPath: () => ""
});

export function ConnectionHandler({children}: {children: React.ReactNode}) {
    // context variables
    const [connected, setConnected] = useState(false);
    const [started, setStarted] = useState(false);
    const [devMode, setDevMode] = useState(false);
    const [ip, setIp] = useState("Unknown");
    const [healthChecking, setHealthChecking] = useState(false);

    const connectedOnce = useRef(false); // maybe change to state

    const checkConnection = async (inputIp: string) => {
        if (inputIp === "Unknown") { return false; } // use inputIp to prevent stale variables
        try {
            const response = await fetch("http://" + inputIp + "/api/health"); // don't use getPath() here, ip state can become stale

            if (response.ok) { connectedOnce.current = true; }

            return response.ok
        } catch (error) {
            return false;
        }
    }

    // health checking loop
    useEffect(() => {
        if (!healthChecking || !started) { return };

        let cancel = false;

        const loop = async function() {
            while (!cancel) {
                const test: boolean = await checkConnection(ip);
                console.log(test)
                if (cancel) { break; };

                setConnected(test);
                await delay(5000);
            }
        }

        loop();

        return () => {
            cancel = true;
        }

    },[healthChecking, ip, started])

    const start = async function() {
        const tempDevMode = await window.electron.isDev()
        setDevMode(tempDevMode)

        while (true) {
            const foundIp = "127.0.0.1" //await window.electron.discover();

            if (foundIp !== null) {
                setIp(foundIp);

                const isValid = await checkConnection(foundIp);
                if (isValid) {
                    setConnected(true);
                    setHealthChecking(true);
                    break;
                }
            }
            await delay(2000);
        }
    }

    const startConnection = async function() {
        if (!started) {
            setStarted(true);
            start();
        }
    };

    const getPath = function(path: string) {
        return "http://" + ip + path;
    }

    return (
        <ConnectionContext.Provider value={{connected, devMode, ip, startConnection, started, getPath}}>
            {children}
        </ConnectionContext.Provider>
    )
}