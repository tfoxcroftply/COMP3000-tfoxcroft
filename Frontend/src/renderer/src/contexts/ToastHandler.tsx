import { createContext, useState } from "react";
import Toast from "@renderer/components/Toast";

type ToastContextType = { // declare types
    showToast: (text: string) => void,
}

export const ToastContext = createContext<ToastContextType>({
    showToast: () => {}
});

export function ToastHandler({children}: {children: React.ReactNode}) {

    const [text, setText] = useState<string | undefined>(undefined);
    const [show, setShow] = useState<boolean>(false);
    const [activeTimeout, setActiveTimeout] = useState<number | undefined>(undefined)

    const cancelToast = function(hide: boolean = false) {
        if (activeTimeout !== undefined) {
            clearTimeout(activeTimeout);
        }
        if (hide) {
            setShow(false);
        }
    }

    const showToast = function(newText: string) {
        if (typeof(newText) !== "string") { return; }

        setText(newText);
        setShow(true);

        cancelToast();

        setActiveTimeout(setTimeout(() => {
            setShow(false);
        }, 10000));
    }

    return (
        <ToastContext.Provider value={{showToast}}>
            {children}
            <Toast text={text} show={show} onClick={() => cancelToast(true)}/>
        </ToastContext.Provider>
    )
}