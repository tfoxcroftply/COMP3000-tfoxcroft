import { app, BrowserWindow, ipcMain } from "electron"
import { join } from "path"
import { is } from "@electron-toolkit/utils"

import { Bonjour } from "bonjour-service"
const discoveryTimeout = 30; // seconds

const bonjour = new Bonjour();
let hostIp = -1; // server tracking, might change method

const createWindow = () => {
	const window = new BrowserWindow({
		width: 960,
		height: 720,
		resizable: false,
		webPreferences: {
			nodeIntegration: false,
			contextIsolation: true,
			preload: join(__dirname, '../preload/index.js'),
		},
	})

	window.setMenuBarVisibility(false);
	//window.loadFile(path.join(__dirname, "index.html"));

	if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
		window.loadURL(process.env['ELECTRON_RENDERER_URL'])
	} else {
		window.loadFile(join(__dirname, '../renderer/index.html'))
	}
}

ipcMain.handle("connection-discover",() => {
	return new Promise(resolve => { // doesnt resolve properly yet
		const search = bonjour.find({} as any, service => {
			console.log(service); // temporary debug print
		})
		
		setTimeout(() => {
			search.stop();
			resolve(null);
		}, discoveryTimeout * 1000);
	})
})

ipcMain.handle("connection-test",() => {
	console.log("Testing connection."); // temporary
})

ipcMain.handle("dev-environment",() => {
	return is.dev
})

app.whenReady().then(() => {
	createWindow();
})