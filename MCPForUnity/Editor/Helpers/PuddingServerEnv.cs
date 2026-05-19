using System.Collections.Generic;
using MCPForUnity.Editor.Constants;
using UnityEditor;

namespace MCPForUnity.Editor.Helpers
{
    /// <summary>
    /// PuddingUnityMCP fork: builds the env-var dictionary that should be exported
    /// to the spawned Python MCP server, based on the user's EditorPrefs choices.
    ///
    /// All entries are opt-in. When the user keeps defaults the dictionary is empty
    /// and the server behaves identically to upstream.
    /// </summary>
    internal static class PuddingServerEnv
    {
        internal const string DefaultLang = "en";
        internal const bool DefaultOptimize = true;
        internal const string OptimizePolicy = "semantic_compression";
        internal const int OptimizeThresholdTokens = 1200;

        public static string CurrentLang
        {
            get => EditorPrefs.GetString(EditorPrefKeys.PuddingLang, DefaultLang);
            set => EditorPrefs.SetString(EditorPrefKeys.PuddingLang, value ?? DefaultLang);
        }

        public static bool OptimizeEnabled
        {
            get => EditorPrefs.GetBool(EditorPrefKeys.PuddingOptimize, DefaultOptimize);
            set => EditorPrefs.SetBool(EditorPrefKeys.PuddingOptimize, value);
        }

        /// <summary>
        /// Compose the env-var dictionary to inject into the server launch script.
        /// Returns an empty dictionary when every setting matches the upstream default.
        /// </summary>
        public static IDictionary<string, string> BuildEnv()
        {
            var env = new Dictionary<string, string>();

            var lang = CurrentLang;
            if (!string.IsNullOrEmpty(lang) && lang != DefaultLang)
            {
                env["UNITY_MCP_LANG"] = lang;
            }

            if (OptimizeEnabled)
            {
                env["UNITY_MCP_RESPONSE_POLICY"] = OptimizePolicy;
                env["UNITY_MCP_RESPONSE_THRESHOLD_TOKENS"] = OptimizeThresholdTokens.ToString();
            }

            return env;
        }
    }
}
