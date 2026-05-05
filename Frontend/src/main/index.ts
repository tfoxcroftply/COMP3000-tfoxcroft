import { app, BrowserWindow, ipcMain } from "electron"
import { join } from "path"
import { is } from "@electron-toolkit/utils"
import { Bonjour } from "bonjour-service"

// variables
const forceConnection = true; // forces device search in dev mode
const discoveryTimeout = 30; // seconds

const bonjour = new Bonjour();

const createWindow = () => {
	const window = new BrowserWindow({
		width: 960,
		height: 720,
		resizable: false,
		title: "temperaturenet",
		webPreferences: {
			nodeIntegration: false,
			contextIsolation: true,
			preload: join(__dirname, '../preload/index.js'), // keep as js not ts
		},
	})

	window.setMenuBarVisibility(false);

	if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
		window.loadURL(process.env['ELECTRON_RENDERER_URL'])
	} else {
		window.loadFile(join(__dirname, '../renderer/index.html'))
	}
}

ipcMain.handle("connectionDiscover",() => {
	return new Promise<string | null>(resolve => { // doesnt resolve properly yet
		if (is.dev && !forceConnection) {
			resolve("127.0.0.1"); 
			return;
		}

		const search = bonjour.find({type: "tftemperaturenet"} as any, service => {
			console.log(service)

			search.stop()
			resolve("temperaturenet.local")
		});
		
		setTimeout(() => {
			search.stop();
			resolve(null);
		}, discoveryTimeout * 1000);
	})
})

ipcMain.handle("isDev",() => {
	return is.dev
})

app.whenReady().then(() => {
	createWindow();
})