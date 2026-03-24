// managed by popup handler, don't import directly

type PopupProperties = {
    text: string,
    show: boolean,
    setShow: (value: boolean) => void,
    callback?: () => void | undefined,
}

import closeIcon from "../assets/icons/close_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"

export default function Popup({text, show, setShow, callback} : PopupProperties) {

    const handleClick = function(useCallback: boolean = false) {
        if (callback && useCallback) {
            callback();
        }
        setShow(false);
    }

    if (!show) { return null; }

    return (
        <div className="fixed inset-0 flex flex-col justify-center">
            <div className="relative z-50 h-fit w-lg p-4 pt-18 space-y-4 bg-white m-auto rounded-2xl">
                <button className="absolute clickable menu-button-container w-fit top-4 right-4" onClick={() => setShow(false)}>
                    <img className="menu-button" src={closeIcon} />
                </button>
                <div className="flex flex-row w-full justify-center">
                    <h1 className="w-[80%] text-center">{text}</h1>
                </div>

                <div className="flex flex-row justify-center w-full pt- space-x-4">
                    { callback !== undefined ?
                    (<>
                        <div className="clickable button-entry-style w-fit p-2" onClick={() => handleClick(true)}>
                            <h1>Confirm</h1>
                        </div>
                        <div className="clickable button-entry-style w-fit p-2" onClick={() => handleClick()}>
                            <h1>Cancel</h1>
                        </div>
                    </>) : 
                    (<>
                        <div className="clickable button-entry-style w-fit p-2" onClick={() => handleClick()}>
                            <h1>Confirm</h1>
                        </div>
                    </>)}
                </div>
            </div>
            <div className="fixed inset-0 bg-black/20" />
        </div>
    )
}