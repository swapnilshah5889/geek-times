/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Optional override for site.json's mediaBaseUrl, e.g. a CDN or S3 URL per environment. */
  readonly VITE_MEDIA_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
