import { createContext, useContext, useEffect, useState } from "react";

import { ConnectionContext } from "./ConnectionHandler";
import { ToastContext } from "./ToastHandler";

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
    deleteNotification: (id: number) => void;
}

export const NotificationContext = createContext<NotificationContextType>({
    notifications: [],
    read: false,
    markAllRead: () => {},
    deleteNotification: (id: number) => {}
});

export function NotificationHandler({children}: {children: React.ReactNode}) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [read, setRead] = useState<boolean>(true)

    const { connected, getPath } = useContext(ConnectionContext);
    const { showToast } = useContext(ToastContext)

    const checkForNotifications = async function () {
        if (!connected) { return }
        try {
            const found = await fetch(getPath("/api/notifications-get"))
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

    useEffect(() => {
        //setRead(false) // for debug
        checkForNotifications(); // runs first without waiting
        const timeout = setInterval(checkForNotifications, 5000);

        return () => clearInterval(timeout)
    },[connected])

    const markAllRead = async function () {
        if (!notifications.some(entry => entry.read === 0)) { return }
        try {
            const request = await fetch(getPath("/api/notifications-read"), {
                method: "PATCH"
            });

            if (request.status === 200) {
                setRead(true)
            }

        } catch {
            // ignore
        }
    }

    const deleteNotification = async function(id: number) {
        const response = await fetch(getPath("/api/notifications-delete"), {
            method: "DELETE",
            body: JSON.stringify(id)
        });

        setNotifications(prev => prev.filter(row => row.id !== id));

        if (response.ok) {
            showToast("Error deleting notification")
            return;
        }

        checkForNotifications();
    }

    const deleteAll = async function () {
        const response = await fetch(getPath("/api/notifications-delete-all"), {
            method: "DELETE"
        });
        if (!response.ok) { return; }
        await checkForNotifications();
    }

    return (
        <NotificationContext.Provider value={{notifications, read, markAllRead, deleteNotification}}>
            {children}
        </NotificationContext.Provider>
    )
}