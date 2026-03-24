export const delay = async function(milliseconds: number) {
    return new Promise(finish => setTimeout(finish, milliseconds));
}