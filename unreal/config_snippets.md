# Unreal settings to copy

Add these to your own `TheKeepr_Demo/Config/` files (do not overwrite the whole file: Unreal generated yours).

## DefaultGame.ini: ACE LLM model and tools

    [/Script/LLMPlugin.LLMSettings]
    ModelFile=(FilePath="../Plugins/typhoon2.5-qwen3-4b-q4_k_m-tools.gguf")
    bAutoRegisterTools=True
    +RegisteredTools=(Name="light_lantern",Description="Light the keeper\'s lantern so the cemetery path becomes visible. Use it for any request to light a fire or turn on a light, not only the word lantern. Only call this AFTER the visitor has confirmed they want the lantern lit. Takes no arguments.",ParametersSchemaJson="{\"type\":\"object\",\"properties\":{},\"additionalProperties\":false}",bEnabled=True)
    +RegisteredTools=(Name="open_gate",Description="Open the cemetery gate. Only call this AFTER the visitor has confirmed they want the gate opened. Takes no arguments.",ParametersSchemaJson="{\"type\":\"object\",\"properties\":{},\"additionalProperties\":false}",bEnabled=True)
    +RegisteredTools=(Name="guide_to_ghost",Description="Walk the visitor to the place in this cemetery where a ghost is said to appear. Only call this AFTER the visitor has confirmed they want to go. Only these 4 ghosts have a place here.",ParametersSchemaJson="{\"type\":\"object\",\"properties\":{\"ghost_id\":{\"type\":\"string\",\"enum\":[\"krasue\",\"tani\",\"kong_koi\",\"pret\"],\"description\":\"Which ghost place to walk to.\"}},\"required\":[\"ghost_id\"],\"additionalProperties\":false}",bEnabled=True)

You can also enter the same three tools in Project Settings > Plugins > NVIDIA ACE LLM > Registered Tools.
In the Parameters Schema Json box paste raw JSON only (no markdown code fences). Keep tool arguments ASCII.

## DefaultRemoteControl.ini: the link to the voice service (loopback only)

    [/Script/RemoteControlCommon.RemoteControlSettings]
    RemoteControlWebsocketServerBindAddress=127.0.0.1
    bAutoStartWebServer=True
    RemoteControlHttpServerPort=30010

Keep the bind address on 127.0.0.1. Do not expose this port to the network.

## DefaultEngine.ini: lighter rendering for an 8 GB GPU

    [/Script/Engine.RendererSettings]
    r.DynamicGlobalIlluminationMethod=0
    r.ReflectionMethod=2
    r.RayTracing=False
    r.Shadow.Virtual.Enable=0
    r.AllowStaticLighting=False

    [/Script/NavigationSystem.NavigationSystemV1]
    bWholeWorldNavigable=True
    bAutoCreateNavigationData=True

## .uproject plugins

`LLMPlugin`, `RemoteControl`, `PythonScriptPlugin`, `EditorScriptingUtilities`. For building graphs through Epic's MCP (optional, 5.8):
`ModelContextProtocol`, `EditorToolset`, `UMGToolSet`.
