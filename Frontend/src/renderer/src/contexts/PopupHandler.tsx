import { createContext, useState } from "react";

import Popup from "@renderer/components/Popup";

type PopupContextType = {
    showPopup: (text: string, callback?: () => void) => void,
    hidePopup: () => void;
}

export const PopupContext = createContext<PopupContextType>({
    showPopup: () => {},
    hidePopup: () => {}
});

export function PopupHandler({children}: {children: React.ReactNode}) {

    const [show, setShow] = useState(false);
    const [text, setText] = useState("");
    const [currentCallback, setCurrentCallback] = useState<(() => void) | undefined>(undefined);


    const showPopup = function(text: string, callback?: () => void) {
        setText(text);
        setCurrentCallback(callback);
        setShow(true)
    }

    const hidePopup = function() {
        setShow(false);
        setText("");
        setCurrentCallback(undefined);
    }

    return (
        <PopupContext.Provider value={{showPopup, hidePopup}}>
            {children}
            <Popup text={text} show={show} setShow={setShow} callback={currentCallback}/>
        </PopupContext.Provider>
    )
}