/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />

declare module "*.svg" {
  const content: string;
  export default content;
}

declare const __BASENAME__: string;
// declare const __PORT__: number;
// declare const __PROXY_TARGET__: string;
// declare const __DOCS_LINK__: string;
declare const __BASE_URL_API__: string;
declare const __BASE_URL_API_V2__: string;
declare const __HEALTH_CHECK_URL__: string;
