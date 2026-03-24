interface Window {
  electron: {
      discover: () => Promise<string | null>;
      isDev: () => Promise<boolean>;
  }
}