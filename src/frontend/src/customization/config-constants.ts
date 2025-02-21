export const BASENAME = "/onlyflow/";
export const PORT = 3000;
export const PROXY_TARGET = "http://127.0.0.1:7860";
export const API_ROUTES = [`^${BASENAME}api/v1/`, `${BASENAME}api/v2/`, `${BASENAME}health`];
export const BASE_URL_API = `${BASENAME}api/v1/`;
export const HEALTH_CHECK_URL = `${BASENAME}health_check`;
export const DOCS_LINK = "https://docs.langflow.org";

export default {
  DOCS_LINK,
  BASENAME,
  PORT,
  PROXY_TARGET,
  API_ROUTES,
  BASE_URL_API,
  HEALTH_CHECK_URL,
};
