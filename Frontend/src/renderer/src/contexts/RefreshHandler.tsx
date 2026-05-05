// normal refreshes seem to break connectionhandler

import { createContext, Fragment, useState, useEffect } from "react";

import { delay } from "@renderer/components/Utils";

type RefreshType = {
    refresh: () => void,
    enableAutoRefresh: (input: boolean) => void
}

export const RefreshContext = createContext<RefreshType>({
    refresh: () => {},
    enableAutoRefresh: () => {},
});

export function RefreshHandler({children} : {children: React.ReactNode}) {
    const [refreshState, setRefreshState] = useState(0);
    const [autoRefresh, setAutoRefresh] = useState(false);

    const refresh = function() {
        setRefreshState(prev => prev == 0 ? 1 : 0)
    }

    useEffect(() => {
        let cancel = false;

        const main = async function() {
            let currentMinute = new Date().getMinutes()

            while (autoRefresh && !cancel) {
                while (currentMinute == new Date().getMinutes()) {
                    await delay(1000);
                }
                if (autoRefresh) { // might be redundant now, but useful for long waits
                    console.log("Automated refresh.")
                    refresh();
                }

                currentMinute = new Date().getMinutes();
            }
        }

        main()

        return () => {
            cancel = true;
        }
    },[autoRefresh])

    const enableAutoRefresh = function(input: boolean) {
        setAutoRefresh(input);
    }

    return (
        <RefreshContext.Provider value={{refresh, enableAutoRefresh}}>
            <Fragment key={refreshState}>
                {children}
            </Fragment>
        </RefreshContext.Provider>
    )
}