const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("electron", {
    discover: () => ipcRenderer.invoke("connection-discover")
});

