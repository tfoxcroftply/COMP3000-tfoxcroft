export const delay = async function(milliseconds: number) {
    return new Promise(finish => setTimeout(finish, milliseconds));
}

export const timestampToDateString = function(timestamp: number, back: number | undefined = undefined) {
    if (back !== undefined) { timestamp -= back }
    return new Date(timestamp).toLocaleDateString("en-GB", {day: "numeric", month: "long", year: "numeric"})
}

export const downloadData = async function() {

}