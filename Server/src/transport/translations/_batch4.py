"""Batch 4 zh_TW translations (auto-generated; merged into zh_TW.py)."""

BATCH_4 = {
    "find_in_file": {
        "description": "使用正規表示式樣式搜尋檔案，並回傳行號和摘錄。",
        "title": "在檔案中尋找",
        "params": {
            "uri": "要在 Assets/ 下搜尋的資源 URI，或 read_resource 支援的檔案路徑格式",
            "pattern": "要搜尋的正規表示式樣式",
            "project_root": "選用的專案根路徑",
            "max_results": "限制結果數量以避免過大的 payload",
            "ignore_case": "不區分大小寫搜尋"
        }
    },
    "run_tests": {
        "description": "非同步啟動 Unity test 執行，並立即回傳 job_id。使用 get_test_job 輪詢進度。",
        "title": "執行 Tests",
        "params": {
            "mode": "要執行的 Unity test 模式",
            "test_names": "要執行的特定 test 完整名稱",
            "group_names": "與 test_names 相同，但允許使用正規表示式",
            "category_names": "用於篩選的 NUnit 分類名稱",
            "assembly_names": "用於篩選 tests 的 Assembly 名稱",
            "include_failed_tests": "僅包含失敗／略過 tests 的詳細資料（預設：false）",
            "include_details": "包含所有 tests 的詳細資料（預設：false）",
            "init_timeout": "初始化逾時時間，單位為毫秒。PlayMode tests 可能因 domain reload 需要更長時間（預設：15000）。建議：PlayMode 使用 120000。"
        }
    },
    "get_test_job": {
        "description": "依 job_id 輪詢非同步 Unity test job。",
        "title": "取得 Test Job",
        "params": {
            "job_id": "run_tests 回傳的 Job id",
            "include_failed_tests": "僅包含失敗／略過 tests 的詳細資料（預設：false）",
            "include_details": "包含所有 tests 的詳細資料（預設：false）",
            "wait_timeout": "若設定，回傳前最多等待這麼多秒讓 tests 完成。可降低輪詢頻率並避免用戶端迴圈偵測。建議：30-60 秒。若 tests 較早完成則立即回傳。"
        }
    },
    "script_apply_edits": {
        "description": "結構化 C# 編輯（方法／類別），具備更安全的邊界 - 優先使用此工具而非原始文字。\n    最佳實務：\n    - 偏好 anchor_* ops，以穩定標記附近的樣式為基礎插入／取代\n    - 使用 replace_method/delete_method 進行整個方法的變更（保持 signatures 平衡）\n    - 避免整個檔案的正規表示式刪除；validators 會防護不平衡的大括號\n    - 對於尾端插入，偏好在最後的大括號（類別結尾）上使用 anchor/regex_replace\n    - 傳入 options.validate='standard' 進行結構檢查；'basic' 用於僅限內部的編輯\n    標準欄位（使用這些精確 key）：\n    - op: replace_method | insert_method | delete_method | anchor_insert | anchor_delete | anchor_replace\n    - className: string（若 method/class ops 省略，預設為 'name'）\n    - methodName: string（replace_method、delete_method 必填）\n    - replacement: string（replace_method、insert_method 必填）\n    - position: start | end | after | before（僅 insert_method）\n    - afterMethodName / beforeMethodName: string（position='after'/'before' 時必填）\n    - anchor: regex string（用於 anchor_* ops）\n    - text: string（用於 anchor_insert/anchor_replace）\n    範例：\n    1) 取代一個方法：\n    {\n        \"name\": \"SmartReach\",\n        \"path\": \"Assets/Scripts/Interaction\",\n        \"edits\": [\n        {\n        \"op\": \"replace_method\",\n        \"className\": \"SmartReach\",\n        \"methodName\": \"HasTarget\",\n        \"replacement\": \"public bool HasTarget(){ return currentTarget!=null; }\"\n        }\n    ],\n    \"options\": {\"validate\": \"standard\", \"refresh\": \"immediate\"}\n    }\n    \"2) 在另一個方法後插入方法：\n    {\n        \"name\": \"SmartReach\",\n        \"path\": \"Assets/Scripts/Interaction\",\n        \"edits\": [\n        {\n        \"op\": \"insert_method\",\n        \"className\": \"SmartReach\",\n        \"replacement\": \"public void PrintSeries(){ Debug.Log(seriesName); }\",\n        \"position\": \"after\",\n        \"afterMethodName\": \"GetCurrentTarget\"\n        }\n    ],\n    }\n    ]",
        "title": "Script 套用編輯",
        "params": {
            "name": "要編輯的 script 名稱",
            "path": "Assets/ 目錄下要編輯的 script 路徑",
            "edits": "要套用到 script 的編輯清單（JSON list 或字串化 JSON）",
            "options": "script 編輯的選項",
            "script_type": "要編輯的 script 類型",
            "namespace": "要編輯的 script namespace"
        }
    },
    "set_active_instance": {
        "description": "為此 client/session 設定作用中的 Unity instance。接受 Name@hash、hash prefix，或連接埠號碼（僅限 stdio）。",
        "title": "設定作用中 Instance",
        "params": {
            "instance": "目標 instance（Name@hash、hash prefix，或 stdio 模式中的連接埠號碼）"
        }
    },
    "unity_docs": {
        "description": "從 docs.unity3d.com 擷取官方 Unity documentation。回傳描述、參數詳細資料、程式碼範例和注意事項。在 unity_reflect 確認類型存在後使用，以便在撰寫實作程式碼前取得使用模式、注意事項和程式碼範例。\n\nActions：\n- get_doc: 擷取 class 或 member 的 ScriptReference docs。需要 class_name。可選 member_name、version。\n- get_manual: 擷取 Unity Manual 頁面。需要 slug（例如 'execution-order'、'urp/urp-introduction'）。可選 version。\n- get_package_doc: 擷取 Package documentation。需要 package、page、pkg_version（例如 package='com.unity.render-pipelines.universal'、page='2d-index'、pkg_version='17.0'）。\n- lookup: 平行搜尋所有 doc sources（ScriptReference + Manual + package docs）。需要 query 或 queries（逗號分隔）。支援 batch：queries='Physics.Raycast,NavMeshAgent,Light2D' 會在一次呼叫中搜尋全部。可選 package + pkg_version 以同時搜尋 package docs。",
        "title": "Unity Docs",
        "params": {
            "action": "要執行的 documentation action。",
            "class_name": "Unity class 名稱（例如 'Physics'、'Transform'）。",
            "member_name": "要查詢的方法或屬性名稱。",
            "version": "Unity version（例如 '6000.0.38f1'）。自動擷取。",
            "slug": "Manual 頁面 slug（例如 'execution-order'）。",
            "package": "Package 名稱（例如 'com.unity.render-pipelines.universal'）。",
            "page": "Package doc 頁面（例如 'index'、'2d-index'）。",
            "pkg_version": "Package version major.minor（例如 '17.0'）。",
            "query": "lookup 的單一搜尋查詢（class 名稱、主題或 slug）。",
            "queries": "batch lookup 的逗號分隔搜尋查詢（例如 'Physics.Raycast,NavMeshAgent,Light2D'）。"
        }
    },
    "unity_reflect": {
        "description": "透過 reflection 檢查 Unity 的即時 C# API。使用此工具在撰寫 C# 程式碼前驗證 classes、methods 和 properties 是否存在，因為訓練資料可能錯誤或過時。\n\nActions：\n- get_type: class 的 member 摘要（僅名稱）。需要 class_name。\n- get_member: 單一 member 的完整 signature 詳細資料。需要 class_name + member_name。\n- search: 在已載入 assemblies 中搜尋類型名稱。需要 query。可選 scope。",
        "title": "Unity Reflect",
        "params": {
            "action": "要執行的 reflection action。",
            "class_name": "完整限定或簡短 C# class 名稱。",
            "member_name": "要檢查的方法、屬性或欄位名稱。",
            "query": "類型名稱搜尋的搜尋查詢。",
            "scope": "搜尋的 Assembly 範圍：unity、packages、project、all。"
        }
    }
}
