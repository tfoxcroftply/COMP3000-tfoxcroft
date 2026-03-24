import { contextBridge, ipcRenderer } from "electron" // moved to es module imports

contextBridge.exposeInMainWorld("electron", {
	discover: () => ipcRenderer.invoke("connectionDiscover"),
	isDev: () => ipcRenderer.invoke("isDev")
});