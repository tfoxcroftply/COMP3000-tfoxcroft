import { useEffect } from "react";
import { useNavigate } from 'react-router-dom'

export default function Loading() {
    const navigate = useNavigate();

    useEffect(() => {
        const temptimer = setTimeout(() => { // for testing
            navigate("/home");
        }, 2000);

        window.electron.discover();

        return () => clearTimeout(temptimer);
    },[navigate])
    return (
        <div className="flex-1 flex flex-col items-center justify-center space-y-10">
            <h1 className="text-3xl font-semibold">Discovering devices</h1>
            <div className="flex flex-row space-x-2 *:inline-block *:h-3 *:w-3 *:rounded-full *:bg-black"> {/* loading dots, animate later*/}
                <span />
                <span />
                <span />
            </div>
        </div>
    )
}

