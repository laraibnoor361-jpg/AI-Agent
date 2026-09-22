# Simple AI Agent

A minimal Streamlit chat app that uses an **AI agent** (via LangChain's
`create_agent`) powered by Groq's `openai/gpt-oss-20b` model.

## Agent vs. Chatbot — what's the difference?

A plain **chatbot** just sends your message straight to an LLM and prints
whatever text comes back. It can only "talk."

An **agent** can also *act*. Before answering, it decides whether it needs
extra information or a calculation, picks the right **tool** to get it,
runs that tool, looks at the result, and only then writes its final answer.
This app's agent has three tools it can choose between:

1. **`web_search`** — searches the web (via `ddgs`) for current information,
   like news or facts released after the model's training cutoff.
2. **`calculator`** — safely evaluates math expressions instead of guessing
   at arithmetic.
3. **`get_current_datetime`** — returns today's real date and time.

So if you ask "What's 348 * 27?" it uses the calculator instead of
hallucinating a number. If you ask "What's the latest news on X?" it
searches the web instead of relying on stale training data. That
tool-picking reasoning loop is what makes it an agent rather than a chatbot.

## Files

- `app.py` — the Streamlit app (UI + tools + agent)
- `requirements.txt` — Python dependencies
- `README.md` — this file

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

You'll need a free Groq API key from [console.groq.com](https://console.groq.com) —
paste it into the sidebar text box when the app opens.

## Deploying on Streamlit Community Cloud

1. Push `app.py` and `requirements.txt` to a GitHub repository (public or
   private is fine).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
3. Click **"New app"**, select your repo, branch, and set the main file
   path to `app.py`.
4. Click **Deploy**. No secrets need to be set on Streamlit Cloud itself —
   each visitor pastes their own Groq API key into the sidebar at runtime,
   so the key is never stored in the repo or on the server.
5. Once deployed, share the app's URL. Anyone using it just needs their own
   Groq API key.

That's it — no server-side configuration required beyond the two files
above.
