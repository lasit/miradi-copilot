# Windows Setup Guide for Miradi Co-Pilot LLM Integration

## Quick Setup for Windows Users

### 1. Install Dependencies
```cmd
pip install anthropic==0.34.0
```

### 2. Configure API Key (Windows)

**Option A: Create .env file (Recommended)**
1. Copy the example file:
   ```cmd
   copy .env.example .env
   ```

2. Edit `.env` file with your API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

**Option B: Set Environment Variable**
```cmd
set ANTHROPIC_API_KEY=your_api_key_here
```

**Option C: PowerShell**
```powershell
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

### 3. Test Integration
```cmd
python test_llm_integration.py
```

### 4. Run Conservation Queries
```cmd
python examples/natural_language_queries.py
```

### 5. Interactive Mode
```cmd
python examples/natural_language_queries.py interactive
```

## Example Conservation Queries

Once setup is complete, you can ask questions like:

- "What threatens the coastal ecosystems?"
- "Which strategies are most effective against poaching?"
- "How does fire management help wildlife?"
- "What indicators track water quality?"
- "Show me threats near forest areas"
- "What is the viability status of our targets?"

## Troubleshooting

### API Key Issues
- Make sure your Anthropic API key starts with `sk-ant-api03-`
- Verify the key is correctly set by running: `python test_llm_integration.py`

### Neo4j Connection
- Ensure Neo4j is running: `docker-compose up -d`
- Load a project first: `python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2`

### Cost Management
- Each query costs approximately $0.02-0.10
- The system tracks costs and shows them in the demo output
- Use interactive mode to control query frequency

## Next Steps

1. Load a Miradi project into Neo4j
2. Run the natural language demo
3. Try your own conservation planning questions
4. Explore the interactive mode for real-time analysis

The system is now ready for natural language conservation planning!
