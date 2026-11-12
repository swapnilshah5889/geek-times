/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Optional override for site.json's mediaBaseUrl, e.g. a CDN or S3 URL per environment. */
  readonly VITE_MEDIA_BASE_URL?: string;
  /** Set to "1" at build time to drop every sample:true item and any reference to one. */
  readonly VITE_HIDE_SAMPLES?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
