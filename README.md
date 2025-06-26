# AI Assistant for Time Series Analysis

A chat-based AI assistant that enables managers to easily analyze IoT time series data from mechanical equipment via API.

## Features

-   Connect to IoT data APIs for real-time data access
-   Intelligent caching for performance optimization
-   Calculate basic statistics (min, max, average, etc.)
-   Chat-based interface for natural language queries
-   Machine status monitoring and data retrieval

## Current System Architecture

```
Frontend (Streamlit)
├── Chat Interface ──────────── GraphChatAgent (LangGraph)
└── Visualization Panel                │
                                       ▼
API Data Access Layer ──────── IoT Data APIs
├── APIConnector                       │
├── CacheManager                       │
└── MetadataManager                    │
├── Anomaly Detection                  │
├── Seasonality Detection              │
├── Basic Statistics                   │
└── Data Preprocessing                 │
                                       ▼
Data Layer ──────────────────── API Data Access (To Be Built)
├── CSV Loader (Current)
└── API Connectors (Planned)
```

#### GraphChatAgent (✅ Implemented)

**Purpose**: Natural language processing and conversation management

-   **Supervisor Pattern**: Intent classification and workflow routing
-   **Message Processing**: Clarification and rewriting of ambiguous requests
-   **Tool Orchestration**: Coordination of information gathering tools
-   **Response Generation**: Natural language response synthesis

#### AnalysisAgent (🚧 To Be Built)

**Purpose**: Execution and orchestration of time series analysis

-   **Analysis Planning**: Decompose complex requests into specific analysis tasks
-   **Tool Orchestration**: Coordinate multiple analysis types (statistics, anomalies, etc.)
-   **Result Synthesis**: Combine and interpret results from multiple analyses
-   **Quality Validation**: Ensure analysis completeness and statistical significance

#### Data Access Layer (🚧 To Be Built)

**Purpose**: Unified interface for data retrieval and management

-   **API Connectors**: Batch processing from various data sources
-   **Data Validation**: Ensure data quality and completeness
-   **Metadata Management**: Track data schemas, time ranges, and source information
-   **Caching**: Performance optimization for repeated requests

## Analysis Workflow

### User Request Processing Flow

```
1. User Query (Natural Language)
   ↓
2. GraphChatAgent
   ├── Intent Classification
   ├── Message Clarification (if needed)
   └── Analysis Request Preparation
   ↓
3. AnalysisAgent
   ├── Analysis Planning & Decomposition
   ├── Data Retrieval (via Data Access Layer)
   ├── Multi-Analysis Execution
   └── Result Synthesis
   ↓
4. GraphChatAgent
   ├── Response Generation
   └── Visualization Coordination
   ↓
5. Frontend Display
   ├── Natural Language Response
   ├── Interactive Charts
   └── Data Tables
```

### Analysis Coverage Strategy

#### Progressive Analysis Pattern

-   **Level 1**: Quick Overview (basic stats, data validation, obvious patterns)
-   **Level 2**: Targeted Analysis (anomalies, seasonality, specific measurements)
-   **Level 3**: Deep Dive (comprehensive multi-column analysis, correlations)

#### Analysis Taxonomy

```
Time Series Analysis Capabilities:
├── Data Validation
│   ├── Missing data detection
│   ├── Data quality assessment
│   └── Time continuity validation
├── Descriptive Analytics
│   ├── Basic statistics (min, max, mean, std, median)
│   ├── Distribution analysis
│   └── Summary reports
├── Diagnostic Analytics
│   ├── Anomaly detection (single and multi-column)
│   ├── Outlier identification
│   └── Pattern deviation analysis
├── Temporal Analytics
│   ├── Seasonality detection
│   ├── Trend analysis
│   └── Cycle identification
└── Comparative Analytics
    ├── Multi-column correlations
    ├── Cross-variable analysis
    └── Benchmark comparisons
```

## Technology Stack

-   **Frontend**: Streamlit for interactive web interface
-   **Backend**: Python with pandas, numpy, scipy for data processing
-   **LLM Integration**: LangChain with Google Gemini for natural language processing
-   **Workflow Management**: LangGraph for agent orchestration
-   **Visualization**: Plotly for interactive charts
-   **Data Processing**: Asynchronous batch processing

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_assitant_tsa
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file with your API keys
   nano .env
   ```
   
   Required environment variables in `.env`:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `LANGSMITH_API_KEY`: Your LangSmith API key (optional, for tracing)
   - `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI models)

4. **Run the application**
   ```bash
   # Start the data server (in one terminal)
   python data_gen/main.py
   
   # Start the frontend (in another terminal)
   streamlit run app.py
   ```

⚠️ **Security Note**: Never commit your `.env` file with real API keys to version control.

### Usage Examples

-   "Show me anomalies in the temperature and pressure data"
-   "What are the basic statistics for all sensors over the last week?"
-   "Is there a daily pattern in the equipment vibration data?"
-   "Validate the data quality and identify any missing values"
-   "Create a comprehensive analysis dashboard for equipment monitoring"
