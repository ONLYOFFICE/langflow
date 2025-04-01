import react from "@vitejs/plugin-react-swc";
import * as dotenv from "dotenv";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import svgr from "vite-plugin-svgr";
import tsconfigPaths from "vite-tsconfig-paths";
import joinPaths from "./src/utils/joinPaths";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const BASENAME = env.VITE_BASENAME || "";
  const PORT = Number(env.VITE_PORT || 3000);
  const PROXY_TARGET = env.VITE_BACKEND_PROXY_URL || "http://127.0.0.1:7860";
  // const DOCS_LINK = env.VITE_DOCS_LINK || "https://docs.langflow.org";

  const API_ROUTES = [
    `^${joinPaths(BASENAME, '/api/v1/')}`,
    `${joinPaths(BASENAME, '/api/v2/')}`,
    `${joinPaths(BASENAME, '/health')}`,
  ];

  const BASE_URL_API = joinPaths(BASENAME, '/api/v1/');
  const HEALTH_CHECK_URL = joinPaths(BASENAME, '/health_check');

  const proxyTargets = API_ROUTES.reduce((proxyObj, route) => {
    proxyObj[route] = {
      target: PROXY_TARGET,
      changeOrigin: true,
      secure: false,
      ws: true,
    };
    return proxyObj;
  }, {});

  console.log({ BASENAME, PORT, PROXY_TARGET, API_ROUTES, BASE_URL_API, HEALTH_CHECK_URL });

  return {
    base: BASENAME || "",
    build: {
      outDir: "build",
    },
    define: {
      "process.env.ACCESS_TOKEN_EXPIRE_SECONDS": JSON.stringify(
        env.ACCESS_TOKEN_EXPIRE_SECONDS,
      ),
      "process.env.CI": JSON.stringify(env.CI),
      __BASENAME__: JSON.stringify(BASENAME),
      __BASE_URL_API__: JSON.stringify(BASE_URL_API),
      __HEALTH_CHECK_URL__: JSON.stringify(HEALTH_CHECK_URL),
    },
    plugins: [react(), svgr(), tsconfigPaths()],
    server: {
      port: PORT,
      proxy: {
        ...proxyTargets,
      },
      allowedHosts: ["langflow.onlyoffice.io"],
    },
  };
});
