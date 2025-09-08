# 🏢 Intelligent ERP Agent System

An advanced ERP (Enterprise Resource Planning) system powered by AI agents, featuring intelligent routing, natural language processing, and comprehensive business data management.

## 🎯 System Architecture

### Agent-Driven Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Router Agent   │───▶│  Sales Agent    │
│  (Natural Lang) │    │  (Query Router)  │    │ (CRM & Leads)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ├──────────────────┐
                                │                  │
                        ┌───────▼────────┐  ┌─────▼──────┐
                        │ Finance Agent  │  │Inventory   │
                        │ (Future)       │  │Agent       │
                        └────────────────┘  │(Future)    │
                                           └────────────┘
```

### Core Components

#### 🤖 **Router Agent** (`backend/agents/simple_router_agent.py`)
- **Responsibility**: Intelligent query routing and agent orchestration
- **Technology**: LangChain ReAct pattern with Google Gemini
- **Features**: 
  - Natural language understanding
  - Context-aware agent selection
  - System information management
  - Graceful error handling

#### 🛍️ **Sales Agent** (`backend/agents/sales_agent.py`)
- **Responsibility**: Customer relationship management and lead handling
- **Tools**:
  - `sales_sql_read`: Query customer/lead data
  - `sales_sql_write`: Create/update customer records
  - `sales_rag_search`: Semantic search across customer data
  - `score_leads`: AI-powered lead scoring
- **Features**:
  - Customer lifecycle management
  - Lead qualification and scoring
  - Order history analysis
  - Revenue reporting

#### 🔧 **MCP (Model Context Protocol) Integration**
- **Tool Registry** (`backend/mcp/tool_registry.py`): Centralized tool management
- **MCP Adapter** (`backend/mcp/mcp_adapter.py`): Protocol compliance layer
- **Features**:
  - Dynamic tool registration
  - Cross-agent tool sharing
  - Standardized tool interfaces

## 🛠️ Tool Integration and MCP Compliance

### Sales Tools (`backend/tools/sales_tools.py`)
```python
# Example: Customer Query Tool
def sales_sql_read(query: str) -> str:
    """Execute read-only SQL queries for customer/lead data"""
    # Implements safe SQL execution with result formatting
    
# Example: Lead Scoring Tool  
def score_leads(criteria: str = "recent") -> str:
    """AI-powered lead scoring and qualification"""
    # Uses business logic to score leads based on multiple factors
```

### MCP Compliance Features
- **Standardized Interfaces**: All tools implement consistent input/output schemas
- **Dynamic Registration**: Tools are automatically discovered and registered
- **Cross-Agent Communication**: Agents can share tools through the MCP registry
- **Error Handling**: Graceful degradation when tools are unavailable

## 💾 Memory Management and Database Usage

### Database Architecture
```
erp.db (Production) / erp_sample.db (Demo)
├── customers (130+ records)
│   ├── Contact information
│   ├── Creation timestamps
│   └── Relationship tracking
├── orders (260+ records)
│   ├── Order details and status
│   ├── Customer associations
│   └── Financial summaries
├── leads (100+ records)
│   ├── Lead scoring data
│   ├── Status tracking
│   └── Source attribution
└── order_items
    ├── Product details
    ├── Pricing information
    └── Quantity tracking
```

### Memory Management Strategy
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Indexed searches and prepared statements
- **Result Caching**: Intelligent caching of frequently accessed data
- **Memory-Safe Operations**: Controlled result set sizes and pagination

### Configuration Management (`backend/config/`)
- **Database Config** (`database.py`): Connection pooling and query optimization
- **LLM Config** (`llm.py`): Multi-provider LLM management (Google Gemini + Ollama fallback)
- **Environment Variables**: Secure API key and database path management

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- SQLite3
- Docker (optional)
- Google API Key (recommended) or Ollama (local alternative)

### Installation

#### Quick Setup with Makefile (Recommended)
```bash
git clone <repository-url>
cd erp_system
make setup  # Creates venv, installs dependencies, creates sample DB
make up     # Starts the system with Docker
```

#### Manual Setup
1. **Clone and Setup**
```bash
git clone <repository-url>
cd erp_system
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
# Create .env file
cp .env.example .env

# Add your API keys
GOOGLE_API_KEY=your_google_api_key_here
DB_PATH=databases/erp_sample.db
```

4. **Initialize Sample Database**
```bash
python create_sample_db.py
```

### Running the System

#### Option 1: Using Makefile (Recommended)
```bash
# Start with Docker (recommended)
make up

# Or start locally without Docker
make start

# View available commands
make help
```

#### Option 2: Manual Local Development
```bash
# Start FastAPI backend
cd backend
python api.py

# In another terminal, start Streamlit frontend
cd frontend  
streamlit run streamlit_app.py
```

#### Option 3: Manual Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access services
# Backend API: http://localhost:8000
# Frontend UI: http://localhost:8501
```

### Usage Examples

#### Natural Language Queries
```python
# Through API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "show recent customers"}'

# Expected Response: Formatted customer list with contact info and order history
```

#### Key ERP Tasks
- **"show recent customers"** → Customer list with revenue data
- **"display leads"** → Lead pipeline with scoring
- **"customer summary"** → Business metrics and KPIs
- **"system info"** → Database status and health check

## 📁 Project Structure

```
erp_system/
├── backend/                    # Core application logic
│   ├── agents/                # AI agent implementations
│   │   ├── sales_agent.py     # Sales and CRM agent
│   │   └── simple_router_agent.py  # Query routing agent
│   ├── config/                # Configuration management
│   │   ├── database.py        # Database connection config
│   │   └── llm.py            # LLM provider configuration
│   ├── mcp/                   # Model Context Protocol
│   │   ├── mcp_adapter.py     # MCP compliance layer
│   │   └── tool_registry.py   # Centralized tool management
│   ├── tools/                 # Business logic tools
│   │   ├── sales_tools.py     # Sales and lead management
│   │   ├── finance_tools.py   # Financial operations (future)
│   │   └── inventory_tools.py # Inventory management (future)
│   ├── tests/                 # Unit and integration tests
│   ├── api.py                 # FastAPI application entry point
│   └── db.py                  # Database utilities
├── frontend/                  # User interface
│   └── streamlit_app.py       # Streamlit web application
├── databases/                 # Database files
│   ├── erp.db                # Production database
│   └── erp_sample.db         # Demo database with sample data
├── logs/                      # Application logs
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Container configuration
├── requirements.txt           # Python dependencies
├── create_sample_db.py        # Sample data generator
└── README.md                  # This documentation
```

## 🛠️ Makefile Commands

The project includes a comprehensive Makefile for easy management:

```bash
# Setup and Installation
make setup       # Install dependencies and create sample database
make build       # Build Docker containers

# Running the System
make up          # Start containers (recommended)
make start       # Start locally without Docker
make down        # Stop containers
make stop        # Stop local processes
make restart     # Restart containers

# Development and Testing
make test        # Run system tests
make demo        # Run interactive demo
make health      # Check system health
make logs        # Show container logs
make shell       # Open shell in backend container

# Maintenance
make clean       # Clean containers and cache files (__pycache__)
make deep-clean  # Clean everything including virtual environment
make status      # Show container status
make help        # Show all available commands
```

## 🧪 Testing

### Using Makefile (Recommended)
```bash
# Run system tests
make test

# Run interactive demo
make demo

# Check system health
make health
```

### Unit Tests
```bash
# Run all tests
python -m pytest backend/tests/

# Test specific components
python -m pytest backend/tests/test_sales_tools.py
python -m pytest backend/tests/test_router.py
```

### Manual Testing
```bash
# Test router agent directly
cd backend
python -c "
from agents.simple_router_agent import create_simple_router_agent
agent = create_simple_router_agent()
result = agent.invoke({'input': 'show recent customers'})
print(result['output'])
"
```

## 🔧 Configuration Options

### LLM Providers
- **Google Gemini** (Primary): High-quality responses, API-based
- **Ollama** (Fallback): Local inference, privacy-focused

### Database Options
- **SQLite** (Default): File-based, zero-configuration
- **PostgreSQL** (Future): Scalable, production-ready

### Deployment Options
- **Local Development**: Direct Python execution
- **Docker**: Containerized deployment
- **Cloud**: Scalable cloud deployment (future)

## 📊 Business Intelligence Features

### Customer Analytics
- Revenue tracking and reporting
- Customer lifecycle analysis
- Order history and patterns
- Geographic and demographic insights

### Lead Management
- AI-powered lead scoring
- Pipeline stage tracking
- Source attribution analysis
- Conversion optimization

### Financial Reporting
- Order value analysis
- Revenue forecasting
- Customer lifetime value
- Profitability metrics

## 🔮 Future Enhancements

### Planned Agents
- **Finance Agent**: Invoice management, payment processing, financial reporting
- **Inventory Agent**: Stock management, procurement, supply chain optimization
- **Analytics Agent**: Advanced reporting, predictive analytics, business intelligence

### Technical Roadmap
- **Enhanced NLP**: Multi-language support, voice interaction
- **Advanced Analytics**: Machine learning models, predictive capabilities
- **Integration APIs**: Third-party system integration, webhook support
- **Mobile Interface**: Responsive design, mobile-first approach

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- **PEP 8**: Python code formatting
- **Type Hints**: Complete type annotations
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for all new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **Ollama Connection**: Ensure Ollama is running locally
- **Database Errors**: Check file permissions and path configuration
- **API Limits**: Monitor Google API usage and quotas

### Getting Help
- **Documentation**: Refer to this README and code comments
- **Issues**: Create GitHub issues for bugs and feature requests
- **Community**: Join our discussion forums for general questions

---

**Built with ❤️ using LangChain, FastAPI, and Google Gemini**
