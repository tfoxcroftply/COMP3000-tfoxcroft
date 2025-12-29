const { app, BrowserWindow, ipcMain } = require("electron")
const { Bonjour } = require("bonjour-service")
const path = require("path")

const discoveryTimeout = 30; // seconds

const bonjour = new Bonjour();
let hostIp = -1; // server tracking, might change method

const createWindow = () => {
    const window = new BrowserWindow({
        width: 800,
        height: 600,
        resizable: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, "preload.js")
        },
    })
    window.setMenuBarVisibility(false);
    window.loadFile(path.join(__dirname, "files/index.html"));
}

ipcMain.handle("connection-discover",() => {
    return new Promise(resolve => { // doesnt resolve yet
        const search = bonjour.find({}, service => {
            console.log(service); // temporary debug print
        })
        
        setTimeout(() => {
            search.stop();
            resolve(null);
        }, discoveryTimeout * 1000);
    })
})

ipcMain.handle("connection-test",() =>{
    console.log("Testing connection."); // temporary
})

app.whenReady().then(() => {
    createWindow();
})