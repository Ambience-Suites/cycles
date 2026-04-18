# Content Data Serial Boxes Specification

## Introduction

Content Data Serial Boxes are the fundamental data packaging mechanism for the Ambience Suites GUI Library. They provide a standardized, serialized format for transmitting, storing, and processing GUI content, state, and configuration data.

## Objectives

- **Standardization:** Provide a uniform data format across all Ambience Suites applications
- **Portability:** Enable content to move seamlessly between platforms and environments
- **Efficiency:** Optimize data size and transmission speed
- **Integrity:** Ensure data authenticity and prevent corruption
- **Versioning:** Support backward compatibility and evolution

## Box Format Specification

### Core Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["box_id", "version", "timestamp", "box_type", "metadata", "payload"],
  "properties": {
    "box_id": {
      "type": "string",
      "description": "Unique identifier for the serial box (UUID v4 format)",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    },
    "version": {
      "type": "string",
      "description": "Serial box format version (semantic versioning)",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "timestamp": {
      "type": "string",
      "description": "Creation timestamp (ISO 8601 format)",
      "format": "date-time"
    },
    "box_type": {
      "type": "string",
      "enum": ["content", "state", "config"],
      "description": "Type of data contained in the box"
    },
    "metadata": {
      "type": "object",
      "required": ["source_repository", "generator", "checksum"],
      "properties": {
        "source_repository": {
          "type": "string",
          "description": "Reference to the source repository"
        },
        "generator": {
          "type": "string",
          "description": "Tool or system that generated the box"
        },
        "checksum": {
          "type": "string",
          "description": "SHA-256 hash of payload for integrity verification (64 hexadecimal characters)",
          "pattern": "^[a-f0-9]{64}$"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Optional tags for categorization"
        },
        "compression": {
          "type": "string",
          "enum": ["none", "gzip", "brotli"],
          "description": "Compression algorithm applied to payload"
        }
      }
    },
    "payload": {
      "type": "object",
      "required": ["content_type", "data"],
      "properties": {
        "content_type": {
          "type": "string",
          "enum": ["ui_component", "narrative", "style", "layout", "animation"],
          "description": "Specific type of content in the payload"
        },
        "permission_ruleset": {
          "type": "string",
          "description": "Content-type permission policy applied during validation"
        },
        "data": {
          "type": "object",
          "description": "The actual serialized content"
        },
        "dependencies": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "box_id": {"type": "string"},
              "type": {"type": "string"},
              "version": {"type": "string"},
              "required": {"type": "boolean"}
            }
          },
          "description": "Other serial boxes required for this content"
        }
      }
    },
    "signature": {
      "type": "string",
      "description": "Optional cryptographic signature for authenticity"
    }
  }
}
```

## Box Types

### 1. Content Boxes

Content boxes package UI components, visual elements, and rendered content from source repositories.

#### Content Box Payload Structure

```json
{
  "content_type": "ui_component",
  "data": {
    "component_id": "button_primary_001",
    "component_class": "Button",
    "properties": {
      "label": "Submit",
      "variant": "primary",
      "size": "medium",
      "disabled": false
    },
    "style": {
      "background_color": "#3b82f6",
      "text_color": "#ffffff",
      "border_radius": "4px",
      "padding": "8px 16px"
    },
    "events": {
      "onClick": "handleSubmit",
      "onHover": "showTooltip"
    },
    "cycles_config": {
      "animation": "fade_in",
      "duration": 300
    }
  },
  "dependencies": [
    {
      "box_id": "palette_001",
      "type": "style",
      "version": "1.0.0",
      "required": true
    }
  ]
}
```

### 2. State Boxes

State boxes capture the current state of GUI components for persistence, debugging, and restoration.

#### State Box Payload Structure

```json
{
  "content_type": "ui_component",
  "data": {
    "component_states": [
      {
        "component_id": "form_login_001",
        "state": {
          "username": "user@example.com",
          "remember_me": true,
          "validation_errors": []
        },
        "timestamp": "2025-11-23T09:05:58.000Z"
      }
    ],
    "global_state": {
      "theme": "dark",
      "locale": "en-US",
      "user_preferences": {
        "animations_enabled": true,
        "reduced_motion": false
      }
    }
  },
  "dependencies": []
}
```

### 3. Config Boxes

Config boxes store configuration, preferences, and settings for GUI behavior and appearance.

#### Config Box Payload Structure

```json
{
  "content_type": "style",
  "data": {
    "palette": {
      "primary": "#3b82f6",
      "secondary": "#8b5cf6",
      "success": "#10b981",
      "warning": "#f59e0b",
      "error": "#ef4444",
      "background": "#ffffff",
      "text": "#1f2937"
    },
    "typography": {
      "font_family": "Inter, sans-serif",
      "base_size": "16px",
      "scale_ratio": 1.25
    },
    "spacing": {
      "base_unit": "4px",
      "scale": [4, 8, 12, 16, 24, 32, 48, 64]
    },
    "animations": {
      "default_duration": 300,
      "default_easing": "ease-in-out"
    }
  },
  "dependencies": [
    {
      "box_id": "nuklear_palette_001",
      "type": "config",
      "version": "1.0.0",
      "required": true
    }
  ]
}
```

## Generation Process

### Step 1: Content Aggregation

```
Input Sources:
├── Cycles Repository (Rendering & Animation)
├── Shooting Script Engine (Narrative Structure)
└── Palette Specification (Visual Styling)
```

### Step 2: Content Processing

1. **Parse Source Data:** Extract relevant content from each repository
2. **Transform:** Convert to GUI-compatible format
3. **Validate:** Ensure content meets specification requirements
4. **Optimize:** Apply compression and optimization techniques

### Step 3: Serialization

1. **Generate Box ID:** Create unique UUID v4 identifier
2. **Package Payload:** Structure data according to box type schema
3. **Calculate Checksum:** Generate SHA-256 hash of payload
4. **Add Metadata:** Include source references and generation info
5. **Optional Signing:** Apply cryptographic signature if required

### Step 4: Validation

```javascript
function validateSerialBox(box) {
  // Verify required fields
  if (!box.box_id || !box.version || !box.timestamp) {
    return false;
  }
  
  // Validate box type
  if (!['content', 'state', 'config'].includes(box.box_type)) {
    return false;
  }
  
  // Verify checksum
  const calculatedChecksum = sha256(JSON.stringify(box.payload));
  if (calculatedChecksum !== box.metadata.checksum) {
    return false;
  }
  
  // Validate dependencies
  for (const dep of box.payload.dependencies || []) {
    if (dep.required && !isBoxAvailable(dep.box_id)) {
      return false;
    }
  }
  
  return true;
}
```

### Step 5: Distribution

Boxes can be distributed through:
- File system storage (local or network)
- HTTP/HTTPS endpoints
- Content Delivery Networks (CDN)
- Message queues
- Database storage

## Integration with Source Repositories

### Cycles Repository Integration

**Purpose:** Rendering and animation data

**Integration Points:**
- Animation cycle definitions → Content boxes
- Rendering pipeline configs → Config boxes
- Frame state data → State boxes

**Example Mapping:**
```
cycles/animations/fade_in.yaml → Content Box (animation type)
cycles/render_config.json → Config Box (rendering settings)
```

### Shooting Script Engine Integration

**Purpose:** Narrative and content structure

**Integration Points:**
- Script templates → Content boxes (narrative structure)
- Scene definitions → Content boxes (layout)
- Character data → Content boxes (UI personas)

**Example Mapping:**
```
ShootingScript/scenes/intro.md → Content Box (narrative type)
ShootingScript/templates/dialog.md → Content Box (ui_component type)
```

### Palette Specification Integration

**Purpose:** Visual styling and theming

**Integration Points:**
- Color palettes → Config boxes (style type)
- Typography specs → Config boxes (style type)
- Material definitions → Config boxes (style type)

**Example Mapping:**
```
Palette/Nuklear_Repository_Outline.md → Config Box (style type)
Palette/themes/dark.json → Config Box (theme settings)
```

## Box Lifecycle

```
┌──────────────┐
│  Generation  │  (Create new box from sources)
└──────┬───────┘
       ↓
┌──────────────┐
│  Validation  │  (Verify integrity and dependencies)
└──────┬───────┘
       ↓
┌──────────────┐
│  Storage     │  (Persist to storage system)
└──────┬───────┘
       ↓
┌──────────────┐
│  Retrieval   │  (Load from storage)
└──────┬───────┘
       ↓
┌──────────────┐
│  Consumption │  (Parse and render in GUI)
└──────┬───────┘
       ↓
┌──────────────┐
│  Caching     │  (Cache for performance)
└──────┬───────┘
       ↓
┌──────────────┐
│  Expiration  │  (Remove from cache/storage)
└──────────────┘
```

## Performance Considerations

### Optimization Strategies

1. **Compression:**
   - Use gzip or brotli for large payloads
   - Store compressed boxes for reduced storage footprint

2. **Caching:**
   - Cache frequently accessed boxes in memory
   - Use CDN for wide distribution
   - Implement cache invalidation strategies

3. **Lazy Loading:**
   - Load dependencies on-demand
   - Stream large boxes progressively
   - Prioritize critical content

4. **Batch Processing:**
   - Generate multiple boxes in parallel
   - Bundle related boxes for transmission
   - Use batch validation for efficiency

### Performance Metrics

- **Box Size:** Target < 100KB per box (uncompressed)
- **Generation Time:** < 100ms per box
- **Validation Time:** < 10ms per box
- **Load Time:** < 50ms per box (cached)

## Security Considerations

### Integrity Protection

- **Checksums:** SHA-256 hashes prevent tampering
- **Validation:** Always validate before consumption
- **Signatures:** Optional cryptographic signatures for authenticity

### Access Control

- Implement authorization for box generation
- Restrict box modification to authorized systems
- Audit box access and modifications

### Safe Deserialization

```javascript
function safeDeserialize(boxData) {
  try {
    // Parse JSON safely
    const box = JSON.parse(boxData);
    
    // Validate schema
    if (!validateSerialBox(box)) {
      throw new Error('Invalid box format');
    }
    
    // Sanitize payload data
    const sanitized = sanitizePayload(box.payload);
    
    return { ...box, payload: sanitized };
  } catch (error) {
    console.error('Deserialization failed:', error);
    return null;
  }
}
```

### Sensitive Data Handling

**State Boxes and Sensitive Information:**

State boxes should NEVER contain sensitive data in plain text. When capturing component state:

1. **Exclude Sensitive Fields:** Password fields, credit card numbers, SSNs, API keys, and tokens should be excluded from state snapshots
2. **Use Placeholders:** For documentation or debugging, use `[REDACTED]` or similar placeholders
3. **Encryption:** If sensitive data must be persisted, use encryption with appropriate key management
4. **Field Filtering:** Implement automatic field filtering based on field types or metadata

```javascript
function sanitizeStateData(componentState, sensitiveFields = ['password', 'ssn', 'credit_card']) {
  const sanitized = { ...componentState };
  
  for (const field of sensitiveFields) {
    if (field in sanitized) {
      sanitized[field] = '[REDACTED]';
    }
  }
  
  return sanitized;
}

// Example usage
function createStateBox(component) {
  const rawState = component.getState();
  const sanitizedState = sanitizeStateData(rawState);
  
  return generateStateBox(sanitizedState);
}
```

**Best Practices:**
- Never log or transmit unencrypted sensitive data
- Implement data classification (public, internal, confidential, secret)
- Use field-level encryption for required sensitive fields
- Regular security audits of state box content
- Implement data retention policies

## Versioning and Compatibility

### Version Policy

- **Major Version (X.0.0):** Breaking changes to box format
- **Minor Version (0.X.0):** Backward-compatible additions
- **Patch Version (0.0.X):** Bug fixes and clarifications

### Compatibility Matrix

| Box Version | GUI Library v1.0 | GUI Library v1.1 | GUI Library v2.0 |
|-------------|------------------|------------------|------------------|
| 1.0.x       | ✓ Full           | ✓ Full           | ✓ Legacy Mode    |
| 1.1.x       | ✗ Not Supported  | ✓ Full           | ✓ Legacy Mode    |
| 2.0.x       | ✗ Not Supported  | ✗ Not Supported  | ✓ Full           |

### Migration Guidelines

When upgrading box versions:
1. Implement backward-compatible parser for older versions
2. Provide migration tools to convert old boxes
3. Maintain deprecation period (minimum 6 months)
4. Document breaking changes clearly

## Implementation Examples

### Example 1: Generate Content Box

```javascript
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

function generateContentBox(componentData, sourceRepo) {
  const payload = {
    content_type: 'ui_component',
    data: componentData,
    dependencies: []
  };
  
  const checksum = crypto
    .createHash('sha256')
    .update(JSON.stringify(payload))
    .digest('hex');
  
  return {
    box_id: uuidv4(),
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    box_type: 'content',
    metadata: {
      source_repository: sourceRepo,
      generator: 'ambience_suites_gui_v1',
      checksum: checksum,
      tags: ['ui', 'component'],
      compression: 'none'
    },
    payload: payload,
    signature: null
  };
}
```

### Example 2: Load and Render Box

```javascript
async function loadAndRender(boxId) {
  // Retrieve box from storage
  const box = await storage.get(boxId);
  
  // Validate integrity
  if (!validateSerialBox(box)) {
    throw new Error('Box validation failed');
  }
  
  // Load dependencies
  for (const dep of box.payload.dependencies || []) {
    if (dep.required) {
      await loadAndRender(dep.box_id);
    }
  }
  
  // Render content
  const renderer = getRenderer(box.payload.content_type);
  await renderer.render(box.payload.data);
}
```

### Example 3: Create State Snapshot

```javascript
function createStateSnapshot(guiComponents) {
  const states = guiComponents.map(component => ({
    component_id: component.id,
    state: component.getState(),
    timestamp: new Date().toISOString()
  }));
  
  const stateBox = generateContentBox(
    {
      component_states: states,
      global_state: getGlobalState()
    },
    'internal_state_capture'
  );
  
  stateBox.box_type = 'state';
  return stateBox;
}
```

## Testing Requirements

### Unit Tests

- Box generation functions
- Validation logic
- Checksum calculation
- Dependency resolution

### Integration Tests

- End-to-end box generation from source repositories
- Box loading and rendering
- Dependency chain resolution
- State persistence and restoration

### Performance Tests

- Box generation throughput
- Validation speed
- Serialization/deserialization performance
- Cache efficiency

## Future Enhancements

- **Streaming Support:** Progressive loading for large boxes
- **Partial Updates:** Delta-based box updates for efficiency
- **Multi-tenancy:** Namespace support for multiple environments
- **Real-time Sync:** WebSocket-based box synchronization
- **Advanced Compression:** Custom compression algorithms
- **Encryption:** End-to-end encryption for sensitive content

---

**Specification Version:** 1.0.0  
**Last Updated:** 2025-11-23  
**Status:** Active
