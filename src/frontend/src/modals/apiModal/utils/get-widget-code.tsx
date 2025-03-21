import { GetCodeType } from "@/types/tweaks";
import joinPaths from "@/utils/joinPaths";

/**
 * Function to get the widget code for the API
 * @param {string} flow - The current flow.
 * @returns {string} - The widget code
 */
export default function getWidgetCode({
  flowId,
  flowName,
  isAuth,
  copy = false,
}: GetCodeType): string {
  const domain = `${window.location.protocol}//${window.location.host}`;

  const baseApiUrl = joinPaths(domain, __BASENAME__);

  return `<script src="https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js"></script>

  <langflow-chat
    window_title="${flowName}"
    flow_id="${flowId}"
    host_url="${baseApiUrl}"
    ${!isAuth ? `api_key="..."` : ""}
  ></langflow-chat>`;
}
