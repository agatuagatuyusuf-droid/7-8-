# C# Runtime / Python Runtime Switch

## Overview

AutoDoor Pro supports two behavior tree runtimes:

1. **Python Runtime** (default) - The original runtime, supports all nodes
2. **C# Core Runtime** (experimental) - New high-performance runtime via CoreService

## How to Enable

### Via Settings UI

1. Open Settings
2. Go to "Runtime" section
3. Check "Use C# Core Runtime (Experimental)"
4. Restart the application

### Via Configuration File

Edit `config.json` (located in `%APPDATA%/AutoDoorPro/`):

```json
{
  "runtime": {
    "use_csharp_core": true
  }
}
```

### Via Environment Variable

```bash
set AUTODOOR_USE_CSHARP_CORE=1
```

## Node Support

### Fully Supported Nodes

| Node Type | Python | C# Core |
|---|---|---|
| StartNode | ✅ | ✅ |
| SequenceNode | ✅ | ✅ |
| SelectorNode | ✅ | ✅ |
| DelayNode | ✅ | ✅ |
| LogStatusNode | ✅ | ✅ |
| SetVariableNode | ✅ | ✅ |
| VariableConditionNode | ✅ | ✅ |
| ColorConditionNode | ✅ | ✅ |

### Partial Support (C# Core)

| Node Type | Python | C# Core |
|---|---|---|
| ImageConditionNode | ✅ | Partial (requires OpenCvSharp4) |
| OcrConditionNode | ✅ | Partial (via Python worker bridge) |

### Not Yet Implemented (C# Core)

| Node Type | Python | C# Core |
|---|---|---|
| KeyPressNode | ✅ | ✅ |
| MouseClickNode | ✅ | ✅ |
| TextInputNode | ✅ | ✅ |

## Fallback Behavior

When C# Core Runtime encounters a `NODE_NOT_IMPLEMENTED` error:

1. The UI will display a notification: "C# runtime doesn't support node type X. Switch back to Python runtime?"
2. The specific node will fail with a clear error message
3. The tree execution will continue (other nodes unaffected)
4. Logs will record: `Node X not implemented in C# runtime`

To switch back to Python runtime:
- Click the notification's "Switch to Python" button, OR
- Go to Settings and disable "Use C# Core Runtime"

## How It Works

```
Python UI <--TCP IPC (127.0.0.1:19527)--> C# CoreService
                                              |
                                         Behavior Tree Engine
                                              |
                                         RSA-verified License
```

When C# runtime is enabled:
1. UI sends the tree JSON over TCP to CoreService
2. CoreService parses and validates the tree
3. CoreService executes the tree
4. Status and logs are streamed back to UI
5. CoreService handles licensing independently

## Logs

### Python Runtime Logs
- Location: `%APPDATA%/AutoDoorPro/logs/`
- Format: Python logging

### C# Core Runtime Logs
- Location: `%APPDATA%/AutoDoorPro/logs/`
- Access: Via `runtime.logs` IPC command
- Format: JSON array with timestamp, level, message

Logs can be viewed in the UI's Log Panel regardless of which runtime is active.

## Troubleshooting

### CoreService won't start
- Check if port 19527 is available
- Check CoreService dependencies (.NET 8 Runtime)
- Check logs in `%APPDATA%/AutoDoorPro/logs/`

### NODE_NOT_IMPLEMENTED errors
- Switch to Python runtime
- Check which nodes are not supported (see table above)

### License errors
- C# runtime uses the same license cache
- If license is invalid, restart CoreService
- Ensure server URL is configured correctly
