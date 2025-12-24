```mermaid
flowchart TD
    A[User Command] --> B{Command Type?}

    B -->|--load-data| C[Load UBER SEC Filings]
    C --> D[Parse HTML Documents]
    D --> E[Create Vector Indices<br/>2019-2022]
    E --> F[Persist to Storage]

    B -->|--chat| G[Load Vector Indices]
    G --> H[Initialize Google Gemini LLM]
    H --> I[Create Query Tools<br/>Per Year + Sub-Question Engine]
    I --> J[Setup FunctionAgent<br/>with System Prompt]
    J --> K[Start Interactive Chat]

    K --> L{User Input}
    L -->|Question| M[Agent Processes Query<br/>using RAG]
    M --> N[Generate Response<br/>with Context]
    N --> O[Display Answer]
    O --> L

    L -->|exit| P[End Chat Session]

    classDef start fill:#4CAF50,color:#fff
    classDef process fill:#2196F3,color:#fff
    classDef decision fill:#FF9800,color:#fff
    classDef end fill:#f44336,color:#fff

    class A start
    class C,D,E,F,G,H,I,J process
    class B,L decision
    class P end
```</content>
<parameter name="filePath">c:\Users\eddie\OneDrive\Documents\Web Projects\CLI_Chat\flow_diagram.md