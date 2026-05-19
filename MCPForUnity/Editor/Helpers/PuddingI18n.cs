using System.Collections.Generic;
using UnityEngine.UIElements;

namespace MCPForUnity.Editor.Helpers
{
    /// <summary>
    /// PuddingUnityMCP fork: Unity Editor UI localization.
    ///
    /// Call <see cref="Apply(VisualElement)"/> on the root visual element after the
    /// window is built; every Label / Button / Toggle / Foldout text and every
    /// VisualElement.tooltip whose English value is in the translation table will
    /// be swapped to the language returned by
    /// <see cref="PuddingServerEnv.CurrentLang"/>.
    ///
    /// English values (UNITY_MCP_LANG=en) are a complete no-op. Strings not in
    /// the table fall back to English silently.
    /// </summary>
    internal static class PuddingI18n
    {
        // english -> (lang -> translated)
        private static readonly Dictionary<string, Dictionary<string, string>> _zhTW = new()
        {
            ["API Key"] = new() { ["zh_TW"] = "API 金鑰" },
            ["API Key:"] = new() { ["zh_TW"] = "API 金鑰：" },
            ["API key for remote-hosted MCP server authentication"] = new() { ["zh_TW"] = "遠端 MCP server 驗證用的 API 金鑰" },
            ["API key management is not available for this server. Contact your server administrator."] = new() { ["zh_TW"] = "此 server 不支援 API 金鑰管理。請聯絡你的 server 管理員。" },
            ["Advanced"] = new() { ["zh_TW"] = "進階" },
            ["Advanced Settings"] = new() { ["zh_TW"] = "進階設定" },
            ["Allow HTTP Local to bind on all interfaces (0.0.0.0 / ::). Disabled by default because devices on your LAN may reach MCP tools."] = new() { ["zh_TW"] = "允許 HTTP Local 綁定所有介面（0.0.0.0 / ::）。預設停用，因為 LAN 上其他裝置可能會接觸到 MCP 工具。" },
            ["Allow HTTP Remote over plaintext http/ws. Disabled by default to require HTTPS/WSS."] = new() { ["zh_TW"] = "允許 HTTP Remote 透過明文 http/ws。預設停用，要求使用 HTTPS/WSS。" },
            ["Allow Insecure Remote HTTP:"] = new() { ["zh_TW"] = "允許不安全的 Remote HTTP：" },
            ["Allow LAN Bind (HTTP Local):"] = new() { ["zh_TW"] = "允許 LAN 綁定（HTTP Local）：" },
            ["An API key is required for HTTP Remote. Enter one above."] = new() { ["zh_TW"] = "HTTP Remote 需要 API 金鑰。請在上方輸入。" },
            ["Auto-Start Server on Editor Load:"] = new() { ["zh_TW"] = "Editor 載入時自動啟動 server：" },
            ["Automatically start the local HTTP server and connect the MCP bridge when the Unity Editor opens. Only applies to HTTP transport (stdio always auto-starts)."] = new() { ["zh_TW"] = "Unity Editor 開啟時自動啟動本機 HTTP server 並連上 MCP bridge。僅適用於 HTTP transport（stdio 永遠會自動啟動）。" },
            ["Browse"] = new() { ["zh_TW"] = "瀏覽" },
            ["Browse for uvx executable"] = new() { ["zh_TW"] = "瀏覽 uvx 執行檔" },
            ["Cancel"] = new() { ["zh_TW"] = "取消" },
            ["Capture a 6-angle contact sheet around the scene centre. Default: Assets/Screenshots (configurable in Advanced)."] = new() { ["zh_TW"] = "圍繞場景中心擷取 6 角度組圖。預設：Assets/Screenshots（可在進階設定調整）。" },
            ["Capture a game camera screenshot. Default: Assets/Screenshots (configurable in Advanced)."] = new() { ["zh_TW"] = "擷取 game camera 截圖。預設：Assets/Screenshots（可在進階設定調整）。" },
            ["Capture the active Scene View viewport. Default: Assets/Screenshots (configurable in Advanced)."] = new() { ["zh_TW"] = "擷取目前的 Scene View 視口。預設：Assets/Screenshots（可在進階設定調整）。" },
            ["Capture:"] = new() { ["zh_TW"] = "截圖：" },
            ["Changes apply after reconnecting or re-registering resources."] = new() { ["zh_TW"] = "重新連線或重新註冊 resource 後生效。" },
            ["Changes apply after reconnecting or re-registering tools."] = new() { ["zh_TW"] = "重新連線或重新註冊 tool 後生效。" },
            ["Changes apply next time the MCP server is started."] = new() { ["zh_TW"] = "下次啟動 MCP server 時生效。" },
            ["Claude CLI Path:"] = new() { ["zh_TW"] = "Claude CLI 路徑：" },
            ["Clear"] = new() { ["zh_TW"] = "清除" },
            ["Clear deployment source path"] = new() { ["zh_TW"] = "清除部署來源路徑" },
            ["Clear override and use auto-detection"] = new() { ["zh_TW"] = "清除覆寫，改用自動偵測" },
            ["Clear override and use default PyPI package"] = new() { ["zh_TW"] = "清除覆寫，改用預設 PyPI package" },
            ["Clear override and use the built-in default (Assets/Screenshots)."] = new() { ["zh_TW"] = "清除覆寫，改用內建預設（Assets/Screenshots）。" },
            ["Client Configuration"] = new() { ["zh_TW"] = "用戶端設定" },
            ["Client Project Dir:"] = new() { ["zh_TW"] = "用戶端專案目錄：" },
            ["Client:"] = new() { ["zh_TW"] = "用戶端：" },
            ["Config Path:"] = new() { ["zh_TW"] = "設定檔路徑：" },
            ["Configuration steps not available for this client."] = new() { ["zh_TW"] = "此用戶端沒有對應的設定步驟。" },
            ["Configuration:"] = new() { ["zh_TW"] = "設定：" },
            ["Configure"] = new() { ["zh_TW"] = "設定" },
            ["Configure All Detected Clients"] = new() { ["zh_TW"] = "設定所有偵測到的用戶端" },
            ["Connect"] = new() { ["zh_TW"] = "連線" },
            ["Copy"] = new() { ["zh_TW"] = "複製" },
            ["Copy MCPForUnity to this project's package location"] = new() { ["zh_TW"] = "把 MCPForUnity 複製到此專案的 package 位置" },
            ["Copy a MCPForUnity folder into this project's package location."] = new() { ["zh_TW"] = "把一個 MCPForUnity 資料夾複製到此專案的 package 位置。" },
            ["Create"] = new() { ["zh_TW"] = "建立" },
            ["Debug Logging:"] = new() { ["zh_TW"] = "除錯日誌：" },
            ["Default folder for screenshots from manage_camera / manage_ui."] = new() { ["zh_TW"] = "manage_camera / manage_ui 截圖的預設資料夾。" },
            ["Deploy"] = new() { ["zh_TW"] = "部署" },
            ["Deps"] = new() { ["zh_TW"] = "相依" },
            ["Disable All"] = new() { ["zh_TW"] = "全部停用" },
            ["Disconnected"] = new() { ["zh_TW"] = "已斷線" },
            ["Discovering resources..."] = new() { ["zh_TW"] = "搜尋 resource 中…" },
            ["Discovering tools..."] = new() { ["zh_TW"] = "搜尋 tool 中…" },
            ["Done"] = new() { ["zh_TW"] = "完成" },
            ["EditorPrefs Manager"] = new() { ["zh_TW"] = "EditorPrefs 管理器" },
            ["Enable All"] = new() { ["zh_TW"] = "全部啟用" },
            ["Enable Token Optimization:"] = new() { ["zh_TW"] = "啟用 Token 最佳化：" },
            ["Enable verbose debug logging to the Unity Console."] = new() { ["zh_TW"] = "啟用 Unity Console 的詳細除錯日誌。" },
            ["End Session"] = new() { ["zh_TW"] = "結束 session" },
            ["Error"] = new() { ["zh_TW"] = "錯誤" },
            ["Force Fresh Install:"] = new() { ["zh_TW"] = "強制全新安裝：" },
            ["Get API Key"] = new() { ["zh_TW"] = "取得 API 金鑰" },
            ["HTTP URL:"] = new() { ["zh_TW"] = "HTTP URL：" },
            ["HTTP endpoint URL for the MCP server. Use localhost for local servers."] = new() { ["zh_TW"] = "MCP server 的 HTTP endpoint URL。本機 server 請用 localhost。" },
            ["Install"] = new() { ["zh_TW"] = "安裝" },
            ["Install All"] = new() { ["zh_TW"] = "全部安裝" },
            ["Install All Dependencies"] = new() { ["zh_TW"] = "安裝所有相依套件" },
            ["Install Skills"] = new() { ["zh_TW"] = "安裝 skill" },
            ["Installation Instructions"] = new() { ["zh_TW"] = "安裝說明" },
            ["Installation Steps:"] = new() { ["zh_TW"] = "安裝步驟：" },
            ["Installing..."] = new() { ["zh_TW"] = "安裝中…" },
            ["Invalid Path"] = new() { ["zh_TW"] = "路徑無效" },
            ["Last backup: none"] = new() { ["zh_TW"] = "最近備份：無" },
            ["Local Server:"] = new() { ["zh_TW"] = "本機 server：" },
            ["Log Record (Assets/mcp.log):"] = new() { ["zh_TW"] = "Log 紀錄（Assets/mcp.log）：" },
            ["Log every MCP tool execution (tool, action, status, duration) to Assets/UnityMCP/Log/mcp.log."] = new() { ["zh_TW"] = "把每次 MCP tool 執行（tool、action、狀態、耗時）記錄到 Assets/UnityMCP/Log/mcp.log。" },
            ["MCP For Unity"] = new() { ["zh_TW"] = "MCP For Unity" },
            ["MCP for Unity Setup"] = new() { ["zh_TW"] = "MCP for Unity 設定" },
            ["MCP for Unity requires Python 3.10+ and UV package manager to function."] = new() { ["zh_TW"] = "MCP for Unity 需要 Python 3.10+ 與 UV package manager 才能運作。" },
            ["Manage MCP for Unity EditorPrefs. Useful for development and testing."] = new() { ["zh_TW"] = "管理 MCP for Unity 的 EditorPrefs。開發與測試時很實用。" },
            ["Manual Configuration"] = new() { ["zh_TW"] = "手動設定" },
            ["Manual Server Launch"] = new() { ["zh_TW"] = "手動啟動 Server" },
            ["Max commands per batch:"] = new() { ["zh_TW"] = "每批次最大指令數：" },
            ["No MCP resources discovered."] = new() { ["zh_TW"] = "未找到 MCP resource。" },
            ["No MCP tools discovered."] = new() { ["zh_TW"] = "未找到 MCP tool。" },
            ["No Session"] = new() { ["zh_TW"] = "無 session" },
            ["Not Configured"] = new() { ["zh_TW"] = "未設定" },
            ["Not Found"] = new() { ["zh_TW"] = "找不到" },
            ["Open"] = new() { ["zh_TW"] = "開啟" },
            ["Open File"] = new() { ["zh_TW"] = "開啟檔案" },
            ["Open Python Install Page"] = new() { ["zh_TW"] = "開啟 Python 安裝頁面" },
            ["Open UV Install Page"] = new() { ["zh_TW"] = "開啟 UV 安裝頁面" },
            ["Optional Dependencies"] = new() { ["zh_TW"] = "選用相依套件" },
            ["Override path to uvx executable. Leave empty for auto-detection."] = new() { ["zh_TW"] = "覆寫 uvx 執行檔路徑。留空則自動偵測。" },
            ["Override server source for uvx --from. Leave empty to use default PyPI package. Example local dev: /path/to/unity-mcp/Server"] = new() { ["zh_TW"] = "覆寫 uvx --from 的 server 來源。留空則使用預設 PyPI package。本機開發範例：/path/to/unity-mcp/Server" },
            ["Package Source:"] = new() { ["zh_TW"] = "Package 來源：" },
            ["Pick a Subfolder"] = new() { ["zh_TW"] = "選擇子資料夾" },
            ["Pick a folder inside the project; the path is stored project-relative."] = new() { ["zh_TW"] = "選擇專案內的資料夾；路徑會以專案相對形式儲存。" },
            ["Please pick a subfolder of the project (for example 'Assets/Screenshots' or 'Captures')."] = new() { ["zh_TW"] = "請選擇專案內的子資料夾（例如 'Assets/Screenshots' 或 'Captures'）。" },
            ["Port for Unity's internal MCP bridge socket. Used for stdio transport."] = new() { ["zh_TW"] = "Unity 內部 MCP bridge socket 的 port。stdio transport 使用。" },
            ["Project-Scoped Tools:"] = new() { ["zh_TW"] = "Project-Scoped Tools：" },
            ["PuddingUnityMCP"] = new() { ["zh_TW"] = "PuddingUnityMCP" },
            ["Python"] = new() { ["zh_TW"] = "Python" },
            ["Reconfigure Clients"] = new() { ["zh_TW"] = "重新設定用戶端" },
            ["Refresh"] = new() { ["zh_TW"] = "重新整理" },
            ["Refresh prefs"] = new() { ["zh_TW"] = "重新整理偏好設定" },
            ["Removing..."] = new() { ["zh_TW"] = "移除中…" },
            ["Rescan"] = new() { ["zh_TW"] = "重新掃描" },
            ["Resources"] = new() { ["zh_TW"] = "Resource" },
            ["Restore"] = new() { ["zh_TW"] = "還原" },
            ["Restore the last backup before deployment"] = new() { ["zh_TW"] = "還原部署前的最近備份" },
            ["Resuming..."] = new() { ["zh_TW"] = "恢復中…" },
            ["Run this command in your shell if you prefer to start the server manually."] = new() { ["zh_TW"] = "若你想手動啟動 server，請在 shell 執行此指令。" },
            ["Screenshots Folder:"] = new() { ["zh_TW"] = "截圖資料夾：" },
            ["Script Validation"] = new() { ["zh_TW"] = "Script 驗證" },
            ["Select"] = new() { ["zh_TW"] = "選擇" },
            ["Select MCPForUnity source folder"] = new() { ["zh_TW"] = "選擇 MCPForUnity 來源資料夾" },
            ["Select local server source folder"] = new() { ["zh_TW"] = "選擇本機 server 來源資料夾" },
            ["Server"] = new() { ["zh_TW"] = "Server" },
            ["Server Health:"] = new() { ["zh_TW"] = "Server 健康狀態：" },
            ["Server Source:"] = new() { ["zh_TW"] = "Server 來源：" },
            ["Some tool groups require optional packages. Install them to unlock additional capabilities."] = new() { ["zh_TW"] = "部分 tool group 需要選用 package。安裝後可解鎖額外功能。" },
            ["Start"] = new() { ["zh_TW"] = "啟動" },
            ["Start Server"] = new() { ["zh_TW"] = "啟動 Server" },
            ["Start Session"] = new() { ["zh_TW"] = "開始 session" },
            ["Start or end the MCP session between Unity and the server."] = new() { ["zh_TW"] = "開始或結束 Unity 與 server 之間的 MCP session。" },
            ["Syncing..."] = new() { ["zh_TW"] = "同步中…" },
            ["System Requirements"] = new() { ["zh_TW"] = "系統需求" },
            ["Test"] = new() { ["zh_TW"] = "測試" },
            ["Test the connection between Unity and the MCP server."] = new() { ["zh_TW"] = "測試 Unity 與 MCP server 之間的連線。" },
            ["The configuration file path does not exist."] = new() { ["zh_TW"] = "設定檔路徑不存在。" },
            ["The selected directory does not exist."] = new() { ["zh_TW"] = "選定的目錄不存在。" },
            ["This will install Roslyn DLLs, ProBuilder, Cinemachine, and VFX Graph. Continue?"] = new() { ["zh_TW"] = "將會安裝 Roslyn DLL、ProBuilder、Cinemachine 與 VFX Graph。要繼續嗎？" },
            ["This will remove Roslyn DLLs, ProBuilder, Cinemachine, and VFX Graph. Continue?"] = new() { ["zh_TW"] = "將會移除 Roslyn DLL、ProBuilder、Cinemachine 與 VFX Graph。要繼續嗎？" },
            ["Tool Language:"] = new() { ["zh_TW"] = "工具語言：" },
            ["Tool schema language. 'zh_TW' loads Traditional Chinese descriptions. Changes apply next time the MCP server is started."] = new() { ["zh_TW"] = "Tool schema 語言。'zh_TW' 載入繁體中文描述。下次啟動 MCP server 時生效。" },
            ["Tools"] = new() { ["zh_TW"] = "Tool" },
            ["Transport Mismatch"] = new() { ["zh_TW"] = "Transport 不符" },
            ["Transport:"] = new() { ["zh_TW"] = "Transport：" },
            ["UV Package Manager"] = new() { ["zh_TW"] = "UV Package Manager" },
            ["UVX Path:"] = new() { ["zh_TW"] = "UVX 路徑：" },
            ["Uninstall"] = new() { ["zh_TW"] = "解除安裝" },
            ["Uninstall All"] = new() { ["zh_TW"] = "全部解除安裝" },
            ["Uninstall All Dependencies"] = new() { ["zh_TW"] = "解除安裝所有相依套件" },
            ["Unity Socket Port:"] = new() { ["zh_TW"] = "Unity Socket Port：" },
            ["Unknown"] = new() { ["zh_TW"] = "未知" },
            ["Use this command to launch the server manually:"] = new() { ["zh_TW"] = "使用此指令手動啟動 server：" },
            ["Validation Level:"] = new() { ["zh_TW"] = "驗證等級：" },
            ["When enabled, generated uvx commands add '--no-cache --refresh' before launching (slower startup, but avoids stale cached builds while iterating on the Server)."] = new() { ["zh_TW"] = "啟用時，產生的 uvx 指令會在啟動前加上 '--no-cache --refresh'（啟動較慢，但開發 server 時可避免使用過期的 cache build）。" },
            ["When enabled, large MCP responses are compressed (semantic_compression, threshold ~1200 tokens). Disable to get unmodified upstream responses. Changes apply next time the MCP server is started."] = new() { ["zh_TW"] = "啟用時，大型 MCP 回應會被壓縮（semantic_compression，門檻約 1200 tokens）。停用則得到原始未修改的 upstream 回應。下次啟動 MCP server 時生效。" },
            ["When enabled, register project-scoped tools with HTTP Local and stdio transports. Allows per-project tool customization."] = new() { ["zh_TW"] = "啟用時，會把 project-scoped tool 註冊到 HTTP Local 與 stdio transport。允許每個專案自訂 tool。" },
            ["⚠ Missing dependencies. MCP for Unity requires all dependencies to function."] = new() { ["zh_TW"] = "⚠ 相依套件缺失。MCP for Unity 需要所有相依套件才能運作。" },
            ["✓ All requirements met! MCP for Unity is ready to use."] = new() { ["zh_TW"] = "✓ 所有需求都符合！MCP for Unity 可以開始使用。" },
        };

        /// <summary>Translate <paramref name="english"/> for the active language; falls back to the original.</summary>
        public static string T(string english)
        {
            if (string.IsNullOrEmpty(english)) return english;
            var lang = PuddingServerEnv.CurrentLang;
            if (string.IsNullOrEmpty(lang) || lang == "en") return english;
            if (_zhTW.TryGetValue(english, out var byLang) && byLang.TryGetValue(lang, out var translated))
            {
                return translated;
            }
            return english;
        }

        /// <summary>
        /// Walk <paramref name="root"/> and translate every <see cref="Label.text"/>,
        /// <see cref="Button.text"/>, <see cref="Toggle.text"/>, <see cref="Foldout.text"/>,
        /// and <see cref="VisualElement.tooltip"/> whose English value is in the translation table.
        /// No-op when language is "en".
        /// </summary>
        public static void Apply(VisualElement root)
        {
            if (root == null) return;
            var lang = PuddingServerEnv.CurrentLang;
            if (string.IsNullOrEmpty(lang) || lang == "en") return;

            root.Query<VisualElement>().ForEach(el =>
            {
                if (!string.IsNullOrEmpty(el.tooltip))
                {
                    el.tooltip = T(el.tooltip);
                }
                switch (el)
                {
                    case Label label:
                        if (!string.IsNullOrEmpty(label.text)) label.text = T(label.text);
                        break;
                    case Button button:
                        if (!string.IsNullOrEmpty(button.text)) button.text = T(button.text);
                        break;
                    case Toggle toggle:
                        if (!string.IsNullOrEmpty(toggle.text)) toggle.text = T(toggle.text);
                        break;
                    case Foldout foldout:
                        if (!string.IsNullOrEmpty(foldout.text)) foldout.text = T(foldout.text);
                        break;
                }
            });
        }
    }
}
