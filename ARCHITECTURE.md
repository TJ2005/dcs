# SENTINEL - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Detection Pipeline](#detection-pipeline)
4. [Data Flow](#data-flow)
5. [Component Details](#component-details)
6. [Data Models](#data-models)
7. [Deployment Architecture](#deployment-architecture)
8. [Security Model](#security-model)

---

## System Overview

**SENTINEL** is a lightweight LLM security middleware that acts as a transparent proxy between users and Large Language Models. It provides real-time threat detection, policy enforcement, and output sanitization without requiring any changes to client applications.

### Key Features
- **Multi-Layer Detection** - Rule-based, GLM triage, and Qwen deep analysis
- **Explainability** - Structured threat metadata on every request
- **User-Aware Defense** - Adaptive security based on trust profiles
- **Firewall Modes** - Strict/Balanced/Open operational modes
- **Output Scrubbing** - PII detection and removal via Presidio + Nemotron
- **Real-Time Dashboard** - Live threat monitoring with SSE feed

---

## High-Level Architecture

```mermaid
graph TB
    subgraph Client["Client Application"]
        APP[Application Code]
    end
    
    subgraph Sentinel["SENTINEL Middleware"]
        API[FastAPI Proxy<br/>:8000]
        
        subgraph DetectionPipeline["Detection Pipeline"]
            RULES[Rule Engine<br/>~5ms]
            GLM[GLM 4.5 Air<br/>~200ms]
            QWEN[Qwen3 480B<br/>~800ms]
            ENSEMBLE[Ensemble Scorer]
        end
        
        subgraph PolicyEngine["Policy Engine"]
            POLICIES[Policy Loader]
            FIREWALL[Firewall Mode]
            SESSION[Session Manager]
            USER[User Trust]
        end
        
        subgraph OutputAuditor["Output Auditor"]
            NEMOTRON[Nemotron 9B V2]
            PRESIDIO[Presidio PII]
        end
        
        REDIS[(Redis Cache<br/>Sessions & Config)]
    end
    
    subgraph VictimLLM["Target LLM"]
        LLAMA[Llama 3.3 70B<br/>OpenRouter]
    end
    
    subgraph Dashboard["Threat Dashboard"]
        UI[React Frontend<br/>:3000]
        SSE[SSE Live Feed]
        CHARTS[Charts & Analytics]
        POLICY_UI[Policy Studio]
    end
    
    APP -->|OpenAI Format<br/>POST /v1/chat/completions| API
    API --> RULES
    RULES --> GLM
    GLM -->|score > 3| QWEN
    GLM --> ENSEMBLE
    QWEN --> ENSEMBLE
    
    ENSEMBLE --> POLICIES
    ENSEMBLE --> FIREWALL
    ENSEMBLE --> SESSION
    ENSEMBLE --> USER
    
    SESSION <--> REDIS
    USER <--> REDIS
    FIREWALL <--> REDIS
    
    API -->|Clean Request| LLAMA
    LLAMA -->|Response| NEMOTRON
    NEMOTRON --> PRESIDIO
    PRESIDIO -->|Sanitized| APP
    
    API -->|ThreatEvents| SSE
    SSE --> UI
    UI --> CHARTS
    UI --> POLICY_UI
    
    POLICY_UI -->|Admin Actions| API
    
    style Sentinel fill:#e1f5ff
    style DetectionPipeline fill:#fff4e6
    style PolicyEngine fill:#f3e5f5
    style OutputAuditor fill:#e8f5e9
```

---

## Detection Pipeline

The detection pipeline processes every incoming request through up to 3 layers, combining scores with configurable weights.

```mermaid
flowchart TD
    START([Incoming Request]) --> EXTRACT[Extract User Message<br/>+ Session Context]
    EXTRACT --> RULE_ENGINE
    
    subgraph Layer1["Layer 1: Rule Engine (15% weight)"]
        RULE_ENGINE[Pattern Matching]
        RULE_ENGINE --> R1{Match Found?}
        R1 -->|Yes| R_SCORE[Score: 0-10<br/>Attack Type Detected]
        R1 -->|No| R_CLEAN[Score: 0]
        R_SCORE --> RULE_OUT[Output: score, pattern]
        R_CLEAN --> RULE_OUT
    end
    
    RULE_OUT --> GLM_LAYER
    
    subgraph Layer2["Layer 2: GLM Triage (30% weight)"]
        GLM_LAYER[GLM 4.5 Air<br/>300ms timeout]
        GLM_LAYER --> G1{Response OK?}
        G1 -->|Yes| G_PARSE[Parse JSON Response]
        G1 -->|Timeout| G_FALLBACK[Use Rule Score Only]
        G_PARSE --> G_SCORE[Score: 0-10<br/>Category + Reason]
        G_SCORE --> GLM_OUT[Output: score, category, reason]
        G_FALLBACK --> GLM_OUT
    end
    
    GLM_OUT --> ESCALATE{GLM Score > 3?}
    
    ESCALATE -->|Yes| QWEN_LAYER
    ESCALATE -->|No| SKIP_QWEN[Skip Deep Analysis]
    
    subgraph Layer3["Layer 3: Qwen Deep Analysis (55% weight)"]
        QWEN_LAYER[Qwen3 480B A35B]
        QWEN_LAYER --> Q_CONTEXT[Include:<br/>- Session History<br/>- Active Policies<br/>- User Trust Level]
        Q_CONTEXT --> Q_PARSE[Parse JSON Response]
        Q_PARSE --> Q_SCORE[Score: 0-10<br/>Policy Violations<br/>Sanitized Version]
    end
    
    Q_SCORE --> ENSEMBLE
    SKIP_QWEN --> ENSEMBLE
    
    subgraph Scoring["Ensemble Scoring"]
        ENSEMBLE[Calculate Raw Score]
        ENSEMBLE --> FORMULA["raw = (rule×0.15) + (glm×0.30) + (qwen×0.55)"]
        FORMULA --> SESSION_MULT[Apply Session Factor<br/>adjusted = raw × session_factor]
        SESSION_MULT --> USER_ADJUST[Apply User Trust Adjustment]
        USER_ADJUST --> FIREWALL_CAP[Apply Firewall Mode Cap]
        FIREWALL_CAP --> FINAL[Final Score: 0-100]
    end
    
    FINAL --> ACTION{Determine Action}
    
    ACTION -->|0-29| ALLOW[ALLOW<br/>Forward to LLM]
    ACTION -->|30-54| FLAG[FLAG<br/>Forward + Escalate Session]
    ACTION -->|55-79| SANITIZE[SANITIZE<br/>Rewrite with Qwen]
    ACTION -->|80-100| BLOCK[BLOCK<br/>Return Safe Message]
    
    ALLOW --> UPDATE_SESSION
    FLAG --> UPDATE_SESSION
    SANITIZE --> UPDATE_SESSION
    BLOCK --> UPDATE_SESSION
    
    UPDATE_SESSION[Update Session & User Profile] --> LOG[Log ThreatEvent]
    LOG --> END([Return Response])
    
    style Layer1 fill:#ffebee
    style Layer2 fill:#fff3e0
    style Layer3 fill:#e3f2fd
    style Scoring fill:#f3e5f5
```

---

## Data Flow

### Request Flow (Clean Path)

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Proxy
    participant Rules as Rule Engine
    participant GLM as GLM 4.5 Air
    participant Redis
    participant LLM as Llama 3.3 70B
    participant Nemotron
    participant Presidio
    
    Client->>API: POST /v1/chat/completions
    Note over API: Extract message<br/>+ X-User-ID header
    
    API->>Rules: Analyze message
    Rules-->>API: score: 0, patterns: []
    
    API->>GLM: Triage (300ms timeout)
    GLM-->>API: score: 2, category: benign
    
    Note over API: Ensemble: (0×0.15)+(2×0.30) = 0.6<br/>Session factor: 1.0<br/>Final: 0.6 → ALLOW
    
    API->>Redis: Update session stats
    Redis-->>API: OK
    
    API->>LLM: Forward request
    LLM-->>API: Response text
    
    API->>Nemotron: Audit output
    Nemotron-->>API: safe: true, issues: []
    
    API->>Presidio: Scan for PII
    Presidio-->>API: No PII found
    
    API->>Redis: Log ThreatEvent (ALLOW)
    API-->>Client: Return clean response
    
    Note over Client,Presidio: Total latency: ~210ms
```

### Request Flow (Attack Blocked)

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Proxy
    participant Rules as Rule Engine
    participant GLM as GLM 4.5 Air
    participant Qwen as Qwen3 480B
    participant Redis
    participant Dashboard
    
    Client->>API: POST /v1/chat/completions<br/>"Ignore all instructions..."
    
    API->>Rules: Analyze message
    Rules-->>API: score: 8, pattern: role_override
    
    API->>GLM: Triage (300ms timeout)
    GLM-->>API: score: 9, category: prompt_injection
    
    Note over API: GLM score > 3 → Escalate to Qwen
    
    API->>Qwen: Deep analysis + policies
    Qwen-->>API: score: 10, violation: true
    
    Note over API: Ensemble: (8×0.15)+(9×0.30)+(10×0.55) = 9.4<br/>Normalized to 0-100: 94<br/>Session factor: 1.0<br/>Final: 94 → BLOCK
    
    API->>Redis: Increment session_factor +0.15
    API->>Redis: Update user trust → flagged
    
    API->>Redis: Log ThreatEvent (BLOCK)
    Redis-->>Dashboard: SSE push
    
    API-->>Client: {"error": "Request blocked",<br/>"threat_event": {...}}
    
    Note over Client,Dashboard: Total latency: ~1.2s<br/>Attack prevented ✓
```

---

## Component Details

### 1. Detection Pipeline Components

```mermaid
graph LR
    subgraph RuleEngine["Rule Engine"]
        R1[Base64 Decoder]
        R2[Unicode Normalizer]
        R3[Pattern Matcher]
        R4[Homoglyph Detector]
        
        R1 --> R3
        R2 --> R3
        R3 --> R4
    end
    
    subgraph GLMTriage["GLM Triage"]
        G1[Prompt Template]
        G2[API Call<br/>non-thinking mode]
        G3[JSON Parser]
        G4[Timeout Handler<br/>300ms]
        
        G1 --> G2
        G2 --> G4
        G4 --> G3
    end
    
    subgraph QwenDeep["Qwen Deep Analysis"]
        Q1[Context Builder<br/>Session + Policies]
        Q2[API Call]
        Q3[JSON Parser]
        Q4[Sanitizer<br/>if needed]
        
        Q1 --> Q2
        Q2 --> Q3
        Q3 --> Q4
    end
    
    RuleEngine --> GLMTriage
    GLMTriage -->|score > 3| QwenDeep
```

### 2. Policy Engine

```mermaid
graph TB
    subgraph PolicySystem["Policy Engine"]
        LOADER[Policy Loader<br/>policies.json]
        WATCHER[File Watcher<br/>Hot Reload]
        ENFORCER[Policy Enforcer]
        
        LOADER --> ENFORCER
        WATCHER -->|File Changed| LOADER
    end
    
    subgraph FirewallModes["Firewall Modes"]
        STRICT[Strict Mode<br/>Block: 60<br/>Sanitize: 40<br/>Flag: 20]
        BALANCED[Balanced Mode<br/>Block: 80<br/>Sanitize: 55<br/>Flag: 30]
        OPEN[Open Mode<br/>Block: 95<br/>Sanitize: 80<br/>Flag: 60]
    end
    
    subgraph UserTrust["User Trust System"]
        NEW[New User<br/>Block threshold +10]
        REGULAR[Regular User<br/>Default thresholds]
        FLAGGED[Flagged User<br/>GLM trigger lowered]
        SUSPICIOUS[Suspicious User<br/>Score × 1.2 bonus]
        
        NEW -->|6+ clean turns| REGULAR
        REGULAR -->|2+ FLAG| FLAGGED
        FLAGGED -->|1+ BLOCK| SUSPICIOUS
    end
    
    ENFORCER --> FirewallModes
    ENFORCER --> UserTrust
```

### 3. Session Management

```mermaid
graph TB
    subgraph SessionTracking["Session Tracking"]
        SESSION_ID[Session ID<br/>from X-Session-ID or generated]
        
        subgraph SessionData["Redis: sentinel:session:{id}"]
            SF[session_factor<br/>1.0 → 2.0]
            TC[turn_count]
            ST[suspicious_turns]
            HIST[history: last 10 turns]
        end
        
        SESSION_ID --> SessionData
    end
    
    subgraph Escalation["Escalation Logic"]
        CHECK{Turn score > 30?}
        CHECK -->|Yes| INC[session_factor += 0.15]
        CHECK -->|No| CLEAN_CHECK{5 consecutive<br/>clean turns?}
        CLEAN_CHECK -->|Yes| RESET[session_factor = 1.0]
        CLEAN_CHECK -->|No| MAINTAIN[Keep current factor]
        
        INC --> CAP{factor > 2.0?}
        CAP -->|Yes| CLAMP[Cap at 2.0]
        CAP -->|No| STORE[Store in Redis]
    end
    
    SessionData --> Escalation
```

---

## Data Models

### ThreatEvent Schema

```mermaid
classDiagram
    class ThreatEvent {
        +string request_id
        +datetime timestamp
        +string session_id
        +float score
        +string action
        +string attack_type
        +float confidence
        +string reason
        +string layer_triggered
        +int latency_ms
        +float session_factor
        +string firewall_mode
        +string user_trust_level
        +string message_preview
        +dict metadata
    }
    
    class SessionProfile {
        +string session_id
        +float session_factor
        +int turn_count
        +int suspicious_turns
        +list~dict~ history
        +datetime last_updated
        +int ttl
    }
    
    class UserProfile {
        +string user_id
        +string trust_level
        +int total_turns
        +int clean_turns
        +int flag_count
        +int block_count
        +datetime last_seen
        +int ttl
    }
    
    class Policy {
        +string id
        +string name
        +string description
        +bool enabled
        +int priority
        +datetime created_at
    }
    
    class FirewallConfig {
        +string mode
        +int block_threshold
        +int sanitize_threshold
        +int flag_threshold
        +datetime updated_at
    }
    
    ThreatEvent --> SessionProfile : references
    ThreatEvent --> UserProfile : references
    ThreatEvent --> FirewallConfig : uses
    ThreatEvent --> Policy : may_violate
```

### API Request/Response Models

```mermaid
classDiagram
    class ChatCompletionRequest {
        +string model
        +list~Message~ messages
        +float temperature
        +int max_tokens
        +dict metadata
    }
    
    class Message {
        +string role
        +string content
    }
    
    class ChatCompletionResponse {
        +string id
        +string object
        +int created
        +string model
        +list~Choice~ choices
        +Usage usage
        +ThreatEvent threat_event
    }
    
    class Choice {
        +int index
        +Message message
        +string finish_reason
    }
    
    class AnalyzeRequest {
        +string message
        +string session_id
        +string user_id
    }
    
    class AnalyzeResponse {
        +ThreatEvent threat_event
        +string recommendation
    }
    
    ChatCompletionRequest --> Message : contains
    ChatCompletionResponse --> Choice : contains
    ChatCompletionResponse --> ThreatEvent : includes
    AnalyzeRequest ..> AnalyzeResponse : returns
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph Docker["Docker Compose Environment"]
        subgraph Backend["sentinel-api (Port 8000)"]
            FASTAPI[FastAPI Application]
            WORKERS[Uvicorn Workers]
            
            subgraph Models["Model Clients"]
                GLM_CLIENT[GLM Client]
                QWEN_CLIENT[Qwen Client]
                NEM_CLIENT[Nemotron Client]
            end
            
            subgraph PII["PII Detection"]
                PRESIDIO_ANALYZER[Presidio Analyzer]
                PRESIDIO_ANON[Presidio Anonymizer]
                SPACY[spaCy en_core_web_lg<br/>pre-baked in image]
            end
        end
        
        subgraph Frontend["sentinel-ui (Port 3000)"]
            REACT[React + Vite]
            SSE_CLIENT[SSE Client]
            RECHARTS[Recharts Library]
        end
        
        subgraph Cache["Redis (Port 6379)"]
            REDIS_DATA[(Session Data<br/>User Profiles<br/>Config<br/>Threat Events)]
        end
        
        FASTAPI --> GLM_CLIENT
        FASTAPI --> QWEN_CLIENT
        FASTAPI --> NEM_CLIENT
        FASTAPI --> PRESIDIO_ANALYZER
        PRESIDIO_ANALYZER --> SPACY
        
        FASTAPI <--> REDIS_DATA
        SSE_CLIENT <--> FASTAPI
    end
    
    subgraph External["External Services"]
        OPENROUTER[OpenRouter API<br/>Free Tier]
        NGROK[ngrok Tunnel<br/>Public Demo URL]
    end
    
    GLM_CLIENT --> OPENROUTER
    QWEN_CLIENT --> OPENROUTER
    NEM_CLIENT --> OPENROUTER
    
    NGROK -.->|Proxy| FASTAPI
    
    subgraph Client["Client Applications"]
        WEB[Web App]
        MOBILE[Mobile App]
        CLI[CLI Tool]
    end
    
    WEB --> NGROK
    MOBILE --> NGROK
    CLI --> NGROK
    
    style Backend fill:#e3f2fd
    style Frontend fill:#f3e5f5
    style Cache fill:#fff3e0
    style External fill:#e8f5e9
```

### Container Architecture

```mermaid
graph LR
    subgraph DockerHost["Docker Host"]
        subgraph Network["sentinel-network (bridge)"]
            API_CONTAINER[sentinel-api<br/>Python 3.11<br/>FastAPI + Uvicorn]
            UI_CONTAINER[sentinel-ui<br/>Node 20<br/>React + Vite]
            REDIS_CONTAINER[redis:7-alpine<br/>Persistent Volume]
            
            API_CONTAINER <--> REDIS_CONTAINER
            UI_CONTAINER -->|Proxy /api| API_CONTAINER
        end
        
        VOLUMES[(Docker Volumes)]
        REDIS_CONTAINER <--> VOLUMES
    end
    
    HOST_8000[Host :8000] --> API_CONTAINER
    HOST_3000[Host :3000] --> UI_CONTAINER
    
    style API_CONTAINER fill:#bbdefb
    style UI_CONTAINER fill:#f8bbd0
    style REDIS_CONTAINER fill:#ffecb3
```

---

## Security Model

### Authentication & Authorization

```mermaid
flowchart TD
    REQUEST[Incoming Request] --> ENDPOINT{Endpoint Type?}
    
    ENDPOINT -->|Read Operations| PUBLIC[Public Access<br/>GET /threats<br/>GET /policies<br/>GET /config]
    
    ENDPOINT -->|Write Operations| AUTH_CHECK{X-Sentinel-Admin-Key<br/>Header Present?}
    
    AUTH_CHECK -->|Yes| VALIDATE{Key Valid?}
    AUTH_CHECK -->|No| REJECT_401[401 Unauthorized]
    
    VALIDATE -->|Yes| ALLOW_WRITE[Allow Write<br/>POST /policies<br/>POST /config<br/>POST /policies/:id/toggle]
    VALIDATE -->|No| REJECT_403[403 Forbidden]
    
    PUBLIC --> EXECUTE[Execute Request]
    ALLOW_WRITE --> EXECUTE
    
    style AUTH_CHECK fill:#fff3e0
    style VALIDATE fill:#fff3e0
    style REJECT_401 fill:#ffebee
    style REJECT_403 fill:#ffebee
```

### Threat Detection Layers

```mermaid
graph TB
    subgraph DefenseInDepth["Defense in Depth"]
        L1[Layer 1: Input Validation<br/>Rule-Based Patterns]
        L2[Layer 2: Semantic Triage<br/>GLM Fast Check]
        L3[Layer 3: Deep Analysis<br/>Qwen Policy Enforcement]
        L4[Layer 4: Session Context<br/>Slow-Burn Detection]
        L5[Layer 5: Output Scrubbing<br/>Nemotron + Presidio]
        
        L1 --> L2
        L2 --> L3
        L3 --> L4
        L4 --> L5
    end
    
    subgraph FailSafe["Fail-Safe Mechanisms"]
        F1[GLM Timeout → Rule Score Only]
        F2[Nemotron Timeout → Fail Closed]
        F3[OpenRouter Error → Conservative Block]
        F4[Redis Error → In-Memory Fallback]
    end
    
    style L1 fill:#ffcdd2
    style L2 fill:#f8bbd0
    style L3 fill:#e1bee7
    style L4 fill:#d1c4e9
    style L5 fill:#c5cae9
```

### PII Protection Flow

```mermaid
flowchart LR
    LLM_RESPONSE[LLM Response Text] --> NEMOTRON_SCAN[Nemotron Analysis]
    
    NEMOTRON_SCAN --> PRESIDIO_DETECT[Presidio Entity Detection]
    
    PRESIDIO_DETECT --> ENTITIES{Entities Found?}
    
    ENTITIES -->|Yes| CLASSIFY[Classify:<br/>EMAIL, PHONE, SSN,<br/>CREDIT_CARD, etc.]
    ENTITIES -->|No| CLEAN[Return Original]
    
    CLASSIFY --> REDACT[Presidio Anonymizer<br/>Replace with [REDACTED]]
    
    REDACT --> AUDIT_LOG[Log Original + Redacted<br/>in Audit Trail]
    
    AUDIT_LOG --> RETURN[Return Redacted Response]
    
    style PRESIDIO_DETECT fill:#e8f5e9
    style REDACT fill:#fff3e0
    style AUDIT_LOG fill:#e3f2fd
```

---

## Performance Characteristics

### Latency Breakdown

```mermaid
gantt
    title Request Latency (Benign Path - Clean Request)
    dateFormat X
    axisFormat %Lms
    
    section Input Analysis
    Rule Engine :0, 5
    GLM Triage :5, 205
    
    section Processing
    Ensemble Scoring :205, 210
    
    section LLM Call
    Llama 3.3 70B :210, 1210
    
    section Output Audit
    Nemotron Check :1210, 1710
    Presidio Scan :1710, 1740
    
    section Response
    Format & Return :1740, 1750
```

```mermaid
gantt
    title Request Latency (Attack Path - Deep Analysis)
    dateFormat X
    axisFormat %Lms
    
    section Input Analysis
    Rule Engine :0, 5
    GLM Triage :5, 205
    Qwen Deep Analysis :205, 1005
    
    section Processing
    Ensemble Scoring :1005, 1010
    Session Update :1010, 1025
    
    section Response
    Block Response :1025, 1030
```

### Scalability Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Throughput | 100 req/s | Single instance |
| P50 Latency (benign) | < 300ms | Rule + GLM only |
| P95 Latency (benign) | < 500ms | Including outliers |
| P50 Latency (escalated) | < 1.5s | Full pipeline |
| False Positive Rate | < 2% | Measured on benign corpus |
| False Negative Rate | < 5% | Measured on attack corpus |
| Redis Hit Rate | > 95% | Session cache efficiency |

---

## API Endpoint Map

```mermaid
graph LR
    subgraph Proxy["Proxy Endpoints"]
        P1[POST /v1/chat/completions<br/>Main proxy - OpenAI compatible]
        P2[POST /analyze<br/>Analyze without forwarding]
    end
    
    subgraph Threats["Threat Management"]
        T1[GET /threats<br/>Last 100 events]
        T2[GET /threats/live<br/>SSE stream]
        T3[GET /session/:id<br/>Session history]
    end
    
    subgraph Policies["Policy Management"]
        PO1[GET /policies<br/>List all policies]
        PO2[POST /policies<br/>[AUTH] Add policy]
        PO3[POST /policies/:id/toggle<br/>[AUTH] Enable/disable]
    end
    
    subgraph Config["Configuration"]
        C1[GET /config<br/>Current firewall mode]
        C2[POST /config<br/>[AUTH] Set firewall mode]
    end
    
    subgraph System["System"]
        S1[GET /health<br/>Health check]
    end
    
    style P1 fill:#e3f2fd
    style T2 fill:#fff3e0
    style PO2 fill:#ffebee
    style PO3 fill:#ffebee
    style C2 fill:#ffebee
```

[AUTH REQUIRED] = Requires `X-Sentinel-Admin-Key` header

---

## Technology Stack Deep Dive

### Backend Stack

```mermaid
graph TB
    subgraph Runtime["Python 3.11 Runtime"]
        FASTAPI[FastAPI 0.115+<br/>Async web framework]
        UVICORN[Uvicorn<br/>ASGI server]
        PYDANTIC[Pydantic v2<br/>Data validation]
    end
    
    subgraph HTTP["HTTP Clients"]
        HTTPX[httpx<br/>Async OpenRouter client]
        RETRY[Tenacity<br/>Retry logic]
    end
    
    subgraph ML["ML & NLP"]
        PRESIDIO_A[presidio-analyzer<br/>PII detection]
        PRESIDIO_AN[presidio-anonymizer<br/>PII redaction]
        SPACY_LIB[spaCy 3.7+<br/>NLP engine]
        MODEL[en_core_web_lg<br/>English language model]
    end
    
    subgraph Data["Data Layer"]
        REDIS_CLIENT[redis-py<br/>Session management]
        JSON_LIB[JSON<br/>Serialization]
    end
    
    FASTAPI --> UVICORN
    FASTAPI --> PYDANTIC
    FASTAPI --> HTTPX
    HTTPX --> RETRY
    FASTAPI --> PRESIDIO_A
    PRESIDIO_A --> SPACY_LIB
    SPACY_LIB --> MODEL
    FASTAPI --> REDIS_CLIENT
    
    style FASTAPI fill:#e3f2fd
    style ML fill:#e8f5e9
    style Data fill:#fff3e0
```

### Frontend Stack

```mermaid
graph TB
    subgraph BuildTool["Build System"]
        VITE[Vite 5+<br/>Fast dev server & bundler]
        NODE[Node.js 20 LTS]
    end
    
    subgraph Framework["UI Framework"]
        REACT[React 18<br/>Component library]
        HOOKS[React Hooks<br/>State management]
    end
    
    subgraph Visualization["Data Visualization"]
        RECHARTS[Recharts<br/>Chart library]
        SVG[SVG Rendering]
    end
    
    subgraph Network["Networking"]
        AXIOS[Axios<br/>HTTP client]
        EVENTSOURCE[EventSource<br/>SSE client]
    end
    
    VITE --> NODE
    VITE --> REACT
    REACT --> HOOKS
    REACT --> RECHARTS
    RECHARTS --> SVG
    REACT --> AXIOS
    REACT --> EVENTSOURCE
    
    style VITE fill:#f3e5f5
    style REACT fill:#e3f2fd
    style RECHARTS fill:#fff3e0
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured in `.env`
- [ ] `SENTINEL_ADMIN_KEY` set to strong random value
- [ ] OpenRouter API key valid and funded
- [ ] Docker and Docker Compose installed
- [ ] Ports 8000, 3000, 6379 available

### Build & Test

- [ ] `docker compose build` completes successfully
- [ ] spaCy model pre-baked in image (no runtime download)
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E attack scenarios validated

### Runtime

- [ ] `docker compose up` starts all 3 services
- [ ] Health check returns 200: `curl http://localhost:8000/health`
- [ ] Redis connection confirmed
- [ ] Frontend loads at `http://localhost:3000`
- [ ] SSE stream connects successfully

### Demo Preparation

- [ ] Run `python seed_demo.py` to pre-seed session data
- [ ] Start ngrok tunnel: `ngrok http 8000`
- [ ] Update React `.env` with ngrok URL
- [ ] Test all 6 demo attack scenarios
- [ ] Verify dashboard shows threat events in real-time
- [ ] Practice 3-minute demo script 3 times

---

## Monitoring & Observability

### Metrics to Track

```mermaid
graph TB
    subgraph RequestMetrics["Request Metrics"]
        RM1[Total Requests/sec]
        RM2[Action Distribution<br/>ALLOW / FLAG / SANITIZE / BLOCK]
        RM3[Attack Type Distribution]
        RM4[Latency Percentiles<br/>p50, p95, p99]
    end
    
    subgraph ModelMetrics["Model Performance"]
        MM1[GLM Timeout Rate]
        MM2[Qwen Escalation Rate]
        MM3[Nemotron Fail-Closed Rate]
        MM4[Model Latency per Layer]
    end
    
    subgraph SystemMetrics["System Health"]
        SM1[Redis Hit Rate]
        SM2[Redis Connection Pool]
        SM3[Memory Usage]
        SM4[CPU Usage]
    end
    
    subgraph SecurityMetrics["Security Metrics"]
        SEC1[False Positive Rate]
        SEC2[False Negative Rate]
        SEC3[Session Escalation Rate]
        SEC4[User Trust Distribution]
    end
    
    style RequestMetrics fill:#e3f2fd
    style ModelMetrics fill:#f3e5f5
    style SystemMetrics fill:#fff3e0
    style SecurityMetrics fill:#ffebee
```

---

## Future Enhancements

### Planned Features

1. **Advanced Policy DSL** - JSON-based policy definitions with boolean logic
2. **Multi-Tenant Support** - Isolated policies and configs per organization
3. **Custom Model Integration** - Support for self-hosted models
4. **Webhook Notifications** - Real-time alerts for high-severity threats
5. **A/B Testing Framework** - Test policy changes before production
6. **Behavioral Analytics** - User behavior profiling beyond trust scores
7. **Compliance Reporting** - Auto-generated SOC 2 / GDPR reports
8. **Rate Limiting** - Per-user and per-IP rate limits

### Architecture Evolution

```mermaid
graph TB
    subgraph Current["Current Architecture"]
        C1[Single Instance<br/>Docker Compose]
        C2[In-Process Detection]
        C3[Redis Cache]
    end
    
    subgraph Future["Future Architecture"]
        F1[Kubernetes Deployment<br/>Auto-scaling]
        F2[Distributed Queue<br/>Kafka/RabbitMQ]
        F3[Microservices<br/>Detection / Policy / Audit]
        F4[PostgreSQL<br/>Long-term storage]
        F5[Prometheus + Grafana<br/>Monitoring]
    end
    
    Current -.->|Migration Path| Future
    
    style Current fill:#ffecb3
    style Future fill:#c8e6c9
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Ensemble Scoring** | Weighted combination of multiple detection layer scores |
| **Fail-Closed** | Security policy where errors default to blocking access |
| **Firewall Mode** | Operational mode determining threat score thresholds |
| **GLM** | General Language Model (GLM 4.5 Air - fast triage model) |
| **Homoglyph** | Visually similar characters from different Unicode blocks |
| **Layer Triggered** | The detection layer that contributed most to the final decision |
| **Nemotron** | NVIDIA's LLM for content safety and PII detection |
| **PII** | Personally Identifiable Information |
| **Presidio** | Microsoft's open-source PII detection framework |
| **Qwen** | Alibaba's large language model for deep analysis |
| **Session Factor** | Multiplier that increases with suspicious activity |
| **Slow-Burn Attack** | Multi-turn attack that gradually escalates |
| **SSE** | Server-Sent Events (one-way real-time updates) |
| **ThreatEvent** | Structured log of a security decision |
| **User Trust Level** | Classification of user based on historical behavior |
| **Victim Model** | The target LLM being protected (Llama 3.3 70B) |

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenRouter API](https://openrouter.ai/docs)
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- [spaCy Documentation](https://spacy.io/)
- [Redis Documentation](https://redis.io/docs/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

**Document Version:** 2.0  
**Last Updated:** 2026-04-03  
**Status:** Implementation Ready
