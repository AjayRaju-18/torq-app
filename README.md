---
title: TORQ - Mechanical Engineering Assistant
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 3.50.2
app_file: app.py
pinned: false
---

# TORQ - Mechanical Engineering Assistant

🤖 An AI-powered chatbot for mechanical engineering using RAG (Retrieval Augmented Generation) with GROQ LLM.

## Features

- Upload and process mechanical engineering PDFs
- RAG mode: Query information from uploaded documents
- Chat mode: General mechanical engineering assistant
- Conversation memory
- ChatGPT-style dark theme UI

## Tech Stack

- GROQ API (llama-3.1-8b-instant)
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- Gradio for web interface

## Setup

1. Set environment variable `GROQ_API_KEY` with your GROQ API key
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python app.py`

## Deployment

This app is designed to run on Hugging Face Spaces.
