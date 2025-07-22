# Security Configuration Setup

## Azure OpenAI Credentials

For security reasons, Azure OpenAI credentials are stored separately from the main code.

### Setup Instructions:

1. **Copy the template file:**
   ```bash
   cp config_template.py config.py
   ```

2. **Edit config.py with your actual credentials:**
   - Replace `YOUR_AZURE_OPENAI_ENDPOINT_HERE` with your Azure OpenAI endpoint
   - Replace `YOUR_AZURE_OPENAI_API_KEY_HERE` with your actual API key
   - Replace `YOUR_DEPLOYMENT_NAME_HERE` with your deployment name

3. **Never commit config.py to version control:**
   - The file is already added to `.gitignore`
   - This prevents accidental exposure of sensitive credentials

### File Structure:
- `config_template.py` - Safe template file (can be committed)
- `config.py` - Your actual credentials (never commit this)
- `testting_chatbot.py` - Main application (imports from config.py)

### Security Best Practices:
- Keep `config.py` local only
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage for unauthorized access
