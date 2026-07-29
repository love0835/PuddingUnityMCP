"""_build_instructions + TOOL_GROUPS zh_TW translations."""

INSTRUCTIONS_BY_SCOPE = {
    'project_scoped': """
這個伺服器提供與 Unity Game Engine Editor 互動的 tools。

我有一套動態 tool 系統。請一律先檢查 mcpforunity://custom-tools resource，以確認目前專案有哪些特殊能力可用。

指定 Unity instances：
- 使用 resource mcpforunity://instances 列出啟用中的 Unity 工作階段（Name@hash）。
- 連接多個 instances 時，請在使用 tools/resources 前，以精確的 Name@hash 呼叫 set_active_instance，將整個 session 的 routing 固定到該 instance。若連接多個 instances 且未設定 active instance，伺服器會回傳錯誤。
- 或者，在任何單一 tool 呼叫中傳入 unity_instance 參數，只 routing 該次呼叫（例如 unity_instance="MyGame@abc123"、unity_instance="abc" 表示 hash prefix，或在 stdio mode 中使用 unity_instance="6401" 表示 port number）。這不會變更 session 預設值。

重要工作流程：

Resources vs Tools：
- 使用 RESOURCES 讀取 Editor 狀態（editor_state、project_info、project_tags、tests 等）
- 使用 TOOLS 執行動作與變更（manage_editor 用於 play mode 控制、tag/layer 管理等）
- 使用 tools 修改引擎狀態前，請一律先檢查相關 resources

讀取 resources（使用下方任何 resource 前請先讀這段）：
- Resources 一律以 URI 定址，絕不以名稱定址。Resource 的名稱與 URI「不可」互換：名稱使用底線（例如 editor_state），URI 使用斜線（例如 mcpforunity://editor/state）。不要把名稱的分隔符換掉來拼 URI — 會得到 404。
- 一律從你的 MCP client 的 resource 清單（resources/list）讀取精確的 URI。本說明以名稱提到 resource 時，請到清單中查其 URI，不要用猜的。
- Resource payload 有包裝：內容位於最上層的 `data` 物件之下，所以欄位路徑是 `data.<section>.<field>`（例如 `data.advice.ready_for_tools`），不是最上層欄位。

Script 管理：
- 建立或修改 scripts（透過你自己的 tools 或 `manage_script` tool）後，繼續前請使用 `read_console` 檢查編譯錯誤
- 只有編譯成功後，才能使用新的 Component/type
- 你可以輪詢 `editor_state` resource 的 `isCompiling` 欄位，檢查 domain reload 是否完成

Scene 設定：
- 新 Scene 中一律包含 Camera 與 main Light（Directional Light）
- 使用 `manage_asset` 為可重複使用的 GameObjects 建立 Prefab
- 使用 `manage_scene` 載入、儲存並查詢 Scene 資訊

路徑慣例：
- 除非另有指定，所有路徑都相對於專案的 `Assets/` 資料夾
- 路徑中使用正斜線（/），以維持跨平台相容性

Console 監控：
- 定期檢查 `read_console`，以捕捉錯誤、警告與編譯狀態
- 依 log 類型（Error、Warning、Log）過濾，以聚焦特定問題

Menu Items：
- 讀取 menu items resource 後，使用 `execute_menu_item`
- 這可讓你與 Unity 的選單系統和第三方 tools 互動

Unity API 驗證（需要 'docs' tool group）：
- 啟用 'docs' tool group 時，請使用 `unity_reflect` 與 `unity_docs` 驗證 Unity API 細節，再回答問題或撰寫 C# 程式碼。LLM 訓練資料經常包含不正確、過時或虛構的 Unity APIs。
- 回答 Unity API 問題前：搜尋專案的 Assets（`manage_asset`）並反射 API（`unity_reflect`）進行確認。不要只依賴訓練資料。
- 常見虛構區域：Shader 與 Material（請一律搜尋 Assets 以取得實際 Shader 名稱）、package-specific APIs（Input System、Cinemachine、ProBuilder、NavMesh、URP/HDRP），以及在 Unity versions 之間變更過的 APIs。
- 工作流程：`unity_reflect search` → `unity_reflect get_type` → `unity_reflect get_member` → `unity_docs get_doc`（如果你需要範例／注意事項）。
- 關於 Shader/Material 的問題：推薦前，使用 `manage_asset(action="search", filter_type="Shader")` 找出專案中實際存在的 Shader。

Payload 大小與分頁（重要）：
- 許多 Unity 查詢可能回傳非常大的 JSON。優先使用 **分頁 + 摘要優先** 的呼叫。
- `manage_scene(action="get_hierarchy")`：
  - 使用 `page_size` + `cursor`，並追蹤 `next_cursor` 直到 null。
  - `page_size` 是 **每頁項目數**；建議起點：**50**。
- `manage_gameobject(action="get_components")`：
  - 先從 `include_properties=false`（僅 metadata）與小的 `page_size` 開始（例如 **10-25**）。
  - 只有需要時才請求 `include_properties=true`；讓 `page_size` 保持小（例如 **3-10**），以限制 payload 大小。
- `manage_asset(action="search")`：
  - 使用分頁（`page_size`、`page_number`），並讓 `page_size` 維持適中（例如 **25-50**），避免 token-heavy responses。
  - 除非明確需要 thumbnails，否則保持 `generate_preview=false`（previews 可能包含大型 base64 payloads）。
""",
    'default': """
這個伺服器提供與 Unity Game Engine Editor 互動的 tools。

Custom tools 會在 Unity 連線時註冊為標準 tools。沒有可用的 project-scoped custom tools resource。

指定 Unity instances：
- 使用 resource mcpforunity://instances 列出啟用中的 Unity 工作階段（Name@hash）。
- 連接多個 instances 時，請在使用 tools/resources 前，以精確的 Name@hash 呼叫 set_active_instance，將整個 session 的 routing 固定到該 instance。若連接多個 instances 且未設定 active instance，伺服器會回傳錯誤。
- 或者，在任何單一 tool 呼叫中傳入 unity_instance 參數，只 routing 該次呼叫（例如 unity_instance="MyGame@abc123"、unity_instance="abc" 表示 hash prefix，或在 stdio mode 中使用 unity_instance="6401" 表示 port number）。這不會變更 session 預設值。

重要工作流程：

Resources vs Tools：
- 使用 RESOURCES 讀取 Editor 狀態（editor_state、project_info、project_tags、tests 等）
- 使用 TOOLS 執行動作與變更（manage_editor 用於 play mode 控制、tag/layer 管理等）
- 使用 tools 修改引擎狀態前，請一律先檢查相關 resources

讀取 resources（使用下方任何 resource 前請先讀這段）：
- Resources 一律以 URI 定址，絕不以名稱定址。Resource 的名稱與 URI「不可」互換：名稱使用底線（例如 editor_state），URI 使用斜線（例如 mcpforunity://editor/state）。不要把名稱的分隔符換掉來拼 URI — 會得到 404。
- 一律從你的 MCP client 的 resource 清單（resources/list）讀取精確的 URI。本說明以名稱提到 resource 時，請到清單中查其 URI，不要用猜的。
- Resource payload 有包裝：內容位於最上層的 `data` 物件之下，所以欄位路徑是 `data.<section>.<field>`（例如 `data.advice.ready_for_tools`），不是最上層欄位。

Script 管理：
- 建立或修改 scripts（透過你自己的 tools 或 `manage_script` tool）後，繼續前請使用 `read_console` 檢查編譯錯誤
- 只有編譯成功後，才能使用新的 Component/type
- 你可以輪詢 `editor_state` resource 的 `isCompiling` 欄位，檢查 domain reload 是否完成

Scene 設定：
- 新 Scene 中一律包含 Camera 與 main Light（Directional Light）
- 使用 `manage_asset` 為可重複使用的 GameObjects 建立 Prefab
- 使用 `manage_scene` 載入、儲存並查詢 Scene 資訊

路徑慣例：
- 除非另有指定，所有路徑都相對於專案的 `Assets/` 資料夾
- 路徑中使用正斜線（/），以維持跨平台相容性

Console 監控：
- 定期檢查 `read_console`，以捕捉錯誤、警告與編譯狀態
- 依 log 類型（Error、Warning、Log）過濾，以聚焦特定問題

Menu Items：
- 讀取 menu items resource 後，使用 `execute_menu_item`
- 這可讓你與 Unity 的選單系統和第三方 tools 互動

Unity API 驗證（需要 'docs' tool group）：
- 啟用 'docs' tool group 時，請使用 `unity_reflect` 與 `unity_docs` 驗證 Unity API 細節，再回答問題或撰寫 C# 程式碼。LLM 訓練資料經常包含不正確、過時或虛構的 Unity APIs。
- 回答 Unity API 問題前：搜尋專案的 Assets（`manage_asset`）並反射 API（`unity_reflect`）進行確認。不要只依賴訓練資料。
- 常見虛構區域：Shader 與 Material（請一律搜尋 Assets 以取得實際 Shader 名稱）、package-specific APIs（Input System、Cinemachine、ProBuilder、NavMesh、URP/HDRP），以及在 Unity versions 之間變更過的 APIs。
- 工作流程：`unity_reflect search` → `unity_reflect get_type` → `unity_reflect get_member` → `unity_docs get_doc`（如果你需要範例／注意事項）。
- 關於 Shader/Material 的問題：推薦前，使用 `manage_asset(action="search", filter_type="Shader")` 找出專案中實際存在的 Shader。

Payload 大小與分頁（重要）：
- 許多 Unity 查詢可能回傳非常大的 JSON。優先使用 **分頁 + 摘要優先** 的呼叫。
- `manage_scene(action="get_hierarchy")`：
  - 使用 `page_size` + `cursor`，並追蹤 `next_cursor` 直到 null。
  - `page_size` 是 **每頁項目數**；建議起點：**50**。
- `manage_gameobject(action="get_components")`：
  - 先從 `include_properties=false`（僅 metadata）與小的 `page_size` 開始（例如 **10-25**）。
  - 只有需要時才請求 `include_properties=true`；讓 `page_size` 保持小（例如 **3-10**），以限制 payload 大小。
- `manage_asset(action="search")`：
  - 使用分頁（`page_size`、`page_number`），並讓 `page_size` 維持適中（例如 **25-50**），避免 token-heavy responses。
  - 除非明確需要 thumbnails，否則保持 `generate_preview=false`（previews 可能包含大型 base64 payloads）。
""",
}

GROUP_TRANSLATIONS = {
    'core': '必要的 Scene、script、Asset 與 Editor tools（預設一律啟用）',
    'docs': 'Unity API 反射與文件查詢',
    'vfx': '視覺效果－VFX Graph、Shader、程序式貼圖',
    'animation': 'Animator 控制與 AnimationClip 建立',
    'ui': 'UI Toolkit（UXML、USS、UIDocument）',
    'scripting_ext': 'ScriptableObject 管理',
    'testing': 'Test runner 與 async test jobs',
    'probuilder': 'ProBuilder 3D 建模－需要 com.unity.probuilder package',
    'profiling': 'Unity Profiler session 控制、計數器、記憶體快照與 Frame Debugger',
    'asset_gen': 'AI asset 生成－3D 模型生成／匯入、2D 圖片生成與音訊生成（自帶金鑰）',
}
