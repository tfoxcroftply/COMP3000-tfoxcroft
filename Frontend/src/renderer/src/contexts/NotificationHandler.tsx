import { createContext, useContext, useEffect, useState } from "react";
import { ConnectionContext } from "./ConnectionHandler";

type Notification = {
    id: number;
    text: string;
    notification_type: number;
    read: number;
}

type NotificationContextType = {
    notifications: Notification[];
    read: boolean;
    markAllRead: () => void;
}

export const NotificationContext = createContext<NotificationContextType>({
    notifications: [],
    read: false,
    markAllRead: () => {}
});

export function NotificationHandler({children}: {children: React.ReactNode}) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [read, setRead] = useState<boolean>(true)

    const { connected, getPath } = useContext(ConnectionContext);

    useEffect(() => {
        //setRead(false) // for debug
        const checkForNotifications = async function () {
            if (!connected) { return }
            try {
                const found = await fetch(getPath("/api/get-notifications"))
                if (!found.ok) {
                    console.log("Could not retrieve notifications from API.")
                    return
                }

                const data = await found.json()
                setNotifications(old => { // might prevent elements from constantly recreating
                    return JSON.stringify(old) !== JSON.stringify(data.data) ? data.data : old
                })

                setRead(!data.data.some(entry => entry.read === 0))

                //console.log(Array.isArray(data))
            } catch {
                // ignore
            }
        }

        checkForNotifications(); // runs first without waiting
        const timeout = setInterval(checkForNotifications, 5000);

        return () => clearInterval(timeout)
    },[connected])

    const markAllRead = async function () {
        if (!notifications.some(entry => entry.read === 0)) { return }
        try {
            const request = await fetch(getPath("/api/patch-notifications-read"), {
                method: "PATCH"
            });

            if (request.status === 200) {
                setRead(true)
            }

        } catch {
            // ignore
        }
    }

    const deleteAll = async function () { // unused
        try {
            const request = await fetch(getPath("/api/delete-notifications"), {
                method: "DELETE"
            });
            if (request.status === 200) {
                setNotifications([])
                setRead(true) // nothing left to be unread
            }
        } catch {
            // ignore
        }
    }

    return (
        <NotificationContext.Provider value={{notifications, read, markAllRead}}>
            {children}
        </NotificationContext.Provider>
    )

}