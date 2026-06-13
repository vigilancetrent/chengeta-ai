# GitHub Repository Metadata

Canonical values for the GitHub repository settings (About panel, topics, social preview).
Apply these in **Settings → General** and the **About** sidebar, or via the `gh` CLI below.

## Description

> Chengeta AI is a unified memory and caching platform for AI agents, workflows, and autonomous systems.

## Website

> https://vigilancetrent.github.io/chengeta-ai

## Topics

```
agent-memory
ai-memory
langchain
langgraph
crewai
autogen
agno
caching
memory-layer
vector-cache
embeddings
llm-cache
ai-infrastructure
```

## Social preview image

Upload `assets/brand/github-banner.svg` (export to PNG at 1280×640 first — see
`assets/brand/README.md`).

## Apply with the GitHub CLI

```bash
gh repo edit vigilancetrent/chengeta-ai \
  --description "Chengeta AI is a unified memory and caching platform for AI agents, workflows, and autonomous systems." \
  --homepage "https://vigilancetrent.github.io/chengeta-ai" \
  --add-topic agent-memory,ai-memory,langchain,langgraph,crewai,autogen,agno,caching,memory-layer,vector-cache,embeddings,llm-cache,ai-infrastructure
```
