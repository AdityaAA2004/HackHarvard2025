/// <reference types="vite/client" />
// Helps define the types for environment variables used in Vite
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_ENV: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}