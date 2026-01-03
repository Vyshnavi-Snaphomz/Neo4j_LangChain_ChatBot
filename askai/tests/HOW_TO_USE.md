# How to Use the Real Estate AI Agent

## Two Ways to Run the Agent:

### 1. **Streamlit Web UI** (Recommended - with Memory!)

**Start the app:**
```bash
streamlit run streamlit_app.py
```

**Access the UI:**
- Open your browser to: **http://localhost:8501**
- You'll see a chat interface
- Type your questions in the input box at the bottom
- The agent will remember your conversation!

**Example conversation:**
1. Type: "properties in texas under 600k"
2. See the results in the chat
3. Type: "what about california?" (it remembers the price!)
4. Type: "show me 3 bedrooms" (it remembers state and price!)

---

### 2. **Terminal** (No Memory)

**Start the app:**
```bash
python main.py
```

**Usage:**
- Type your questions at the "User:" prompt
- Press Enter to send
- Agent responds in the terminal
- Type "quit" to exit

**Note:** Terminal version does NOT have conversational memory!

---

## Current Status

✅ Streamlit app is running at: http://localhost:8501  
✅ Conversational memory is enabled  
✅ Context-aware responses work  

## Troubleshooting

**If Streamlit UI doesn't show responses:**
1. Make sure you're accessing http://localhost:8501 in your browser
2. Don't run `main.py` - that's the old terminal version
3. Refresh the browser page
4. Check the terminal for any error messages

**If you see errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that your `.env` file has the correct credentials
- Restart the Streamlit app
