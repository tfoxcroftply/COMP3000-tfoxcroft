// template (example code)
// use https://reactpractice.dev/articles/react-context-example-with-typescript/

import { createContext, useState } from "react";

type TemplateContextType = { // declare types
    value: number;
}

export const PopupContext = createContext<TemplateContextType>({
    value: -1,
});

export function TemplateHandler({children}: {children: React.ReactNode}) {

    const [value, setValue] = useState(-1);

    return (
        <PopupContext.Provider value={{value}}>
            {children}
        </PopupContext.Provider>
    )
}