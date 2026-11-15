---
name: agentrun-setup
description: Install the AgentRun platform, connect a model provider, and guide the user through a first agent in its console. Use when asked to set up, install, or try AgentRun.
---

# Set up AgentRun

AgentRun is an open-source platform that supercharges your agents. It adds self-improvement, durable execution and a control plane on top of your favorite agent harness. Your agents become smarter, more fault tolerant and use fewer tokens with every run. Set up the AgentRun platform on this machine, then help me create and run a first agent from its console. Use the published launcher below. The coding app receiving this prompt is my setup assistant; it does not determine the harness my AgentRun agent uses.

## Reference instructions

- Platform quickstart: https://agentrun.ai/docs/quickstart
- Repository overview: https://github.com/Parcha-ai/agentrun/blob/main/README.md
- Repository setup skill: https://github.com/Parcha-ai/agentrun/blob/main/docs/SKILL.md
- Current server reference: https://github.com/Parcha-ai/agentrun/blob/main/packages/serve/README.md

The website's guides follow current repository source. The launcher, @parcha/agentrun on its 0.4 line, installs its matching server; main-only features may not be in that release yet. Use the running server's capabilities and OpenAPI before applying newer configuration. This setup needs no client library or workflow extension; the clients (@parcha/agentrun-client on npm, parcha-agentrun on PyPI) are for calling the API from code later. Do not combine main's Compose file with an older server image.

## 1. Check the machine

Check macOS or Linux, npm, and Node.js 24.22.3 or newer. If Node needs changing, explain the requirement and use the user's existing version manager when authorized.

Look for an existing AgentRun server and data directory before starting another. Reuse a working installation rather than overwriting it. Do not migrate or delete old data automatically. The default data directory is ~/.agentrun; use a separate --data directory if trying a version incompatible with an existing store.

Docker is optional for the first text-only task. If a shell is wanted, check that Docker is installed, running, and accessible to the server user. Its first box image build may take a few minutes.

## 2. Start the published platform

The interactive command is:

```sh
npx @parcha/agentrun@0.4
```

For an agent-managed process, use the same package with npx --yes and --no-open in the environment's supported persistent terminal/session mechanism. Wait a bounded time for startup and read the address it prints. Do not assume port 7340: the launcher uses the first free port starting there.

Give me that console address. On first visit, I set the owner password. If this is a remote VM, use its existing approved SSH tunnel or private preview; do not expose a new public listener merely to finish setup.

## 3. Configure the model

Have me open Settings → Tool keys → Model keys and save a provider key there. Recommend a capped OpenRouter key as a simple starting point; Anthropic or OpenAI API keys are alternatives. A coding-app subscription is not the server's API key.

Reuse a provider key already configured without revealing it. Never request a secret in chat, print it, place it in instructions, or commit it. A saved console key takes effect without restart; an environment change needs a restart of the server.

Check /v2/capabilities for the model and available harnesses. Pi is included; if another harness is unavailable, report its setup reason. A separate decision-provider key is not required for the first text-only task. Consult the server's decision-workflows section only if we later use typed decision nodes.

## 4. Create and run the first agent

Guide me through Agents → New agent:
- Name: Release notes.
- Harness: Pi for the first run, unless I requested another available harness.
- Instructions: Write concise release notes from the changes I provide. Group them into Added, Changed, and Fixed. Do not invent changes.
- Model: an available configured model.
- Tools: none required.

On its page, choose Start a run with:
"Write release notes: added CSV export to the runs page; fixed the date filter resetting after refresh; renamed workspace settings to Settings."

Review the selected model and spend cap with me before a paid run. Do not start a model call just to check installation. If I explicitly authorize you to run it, use the CLI or API, preserve the cap, and follow the actual run to completion.

## 5. Verify and hand over

Confirm the console opens, the server is healthy, and the model/harness are ready. Once I start the first run, check its actual result, status, and recorded usage; verify it remains in Runs after a reload.

Report separately what is ready and what was actually executed. If the key or paid run is still pending, say so. Give me the console link, data directory, installed launcher version, and the next step. After the first task works, show how to enable Learning for repeated work and inspect what it retains.
