# ERP System - Multi-Agent Chat Assistant

A sophisticated ERP system powered by multiple AI agents with memory capabilities, built with LangChain, Streamlit, and Docker.

## 🚀 Features

- **3 Specialized AI Agents**: Router, Sales, and Analytics agents
- **Memory System**: Persistent conversation and entity memory
- **Chat Interface**: Modern Streamlit-based UI with live updates
- **Database Integration**: SQLite with comprehensive business data
- **Docker Deployment**: Containerized architecture
- **Live Development**: Hot-reload support for development

## 🏗️ Architecture

### Agents
- **Router Agent**: Smart query routing and system management
- **Sales Agent**: Customer management, orders, and CRM operations
- **Analytics Agent**: Data analysis, reporting, and SQL queries

### Memory System
- **RouterGlobalState**: Conversation tracking and routing history
- **SalesEntityMemory**: Customer and sales data persistence
- **AnalyticsReportMemory**: Saved reports and query history

## 🔧 Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Gemini API key

### Setup
1. Clone the repository
2. Copy `.env.example` to `.env` and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
3. Start the system:
   ```bash
   docker compose up -d
   ```
4. Access the chat interface at `http://localhost:8501`

## 💬 Usage Examples

### Sales Agent
```
"show customers" - List recent customers with order history
"Show recent orders" - Display order information
"customer summary" - Customer statistics
```

### Analytics Agent
```
"What's our total revenue?" - Financial reporting
"Show revenue by month" - Time-based analysis
"How many orders do we have?" - Count queries
```

### Router Agent
```
"What's our system status?" - System information
"Show me our top customers" - Smart routing to appropriate agent
```

## 📊 Database Schema

The system includes comprehensive business data:
- **Customers**: 113+ customers with contact information
- **Orders**: 260+ orders with proper relationships
- **Revenue Data**: Multi-year financial records
- **Order Status**: Complete order lifecycle tracking

## 🛠️ Development

### Project Structure
```
erp_system/
├── backend/           # Core agent logic and APIs
│   ├── agents/        # AI agent implementations
│   ├── memory/        # Memory systems
│   ├── tools/         # Business logic tools
│   └── config/        # Configuration management
├── frontend/          # Streamlit web interface
├── databases/         # SQLite database files
└── docker-compose.yml # Container orchestration
```

### Live Development
The system includes volume mounting for live changes - edit files locally and see changes reflected immediately without container restarts.

## 🚨 System Status
- ✅ All agents operational
- ✅ Memory systems active
- ✅ Database connections stable
- ✅ Chat interface functional

## 📈 Performance
- **Total Revenue**: $310,898.07
- **Orders Processed**: 260+
- **Customers Served**: 113+
- **Memory Retention**: Full conversation history

---

*ERP Chat Assistant - Intelligent Business Management Made Simple*
