Slash Commands & CLI Commands in AI Coding Assistants
Claude Code (Anthropic)
Overview: Claude Code is Anthropic’s AI coding assistant that runs in your terminal (and can integrate with VS Code). It supports slash commands (starting with /) for controlling sessions and performing actions, plus user-defined commands and hooks[1][2].
•	Built-in Slash Commands: Key commands include /clear (start a fresh chat, clearing history)[3], /compact (summarize and compress older conversation context)[1][4], /help (list available commands)[5], and various integration commands. For example, /install-github-app installs the Claude GitHub app to enable automatic PR review[6], and /terminal-setup configures your terminal environment for Claude[7]. You can also use /hooks to interactively configure event hooks (triggers that run actions on events like file save)[8][2]. All built-in commands can be listed by typing / in the Claude chat or via the SDK initialization metadata[9].
•	Custom Slash Commands: Claude Code allows you to define custom commands as Markdown files. Create a .claude/commands/ directory in your project (or use ~/.claude/commands for global commands) and add a <command-name>.md file with the prompt content[10][11]. The filename (without extension) becomes the slash command. For example, adding .claude/commands/test.md with content “Please create tests for: $ARGUMENTS” defines a /test command; invoking /test MyButton will prompt Claude to generate tests for “MyButton”[12][13]. Markdown files can include YAML frontmatter to configure tools, description, or model to use[14]. They also support placeholders like $1, $2, or $ARGUMENTS for injecting user arguments[15][16]. Advanced features include embedding file contents via @filename and executing shell commands via ! blocks in the prompt[17][18]. Custom commands are automatically discovered and listed alongside built-ins on session start[19].
•	Usage Example: In a Claude Code terminal session or the VS Code chat, type commands like /clear to reset the conversation[20], or use a custom command (e.g. /refactor src/util.js) to run a stored prompt that refactors the code[21]. Custom slash commands can even be invoked by Claude itself as “tools” (since v1.0.123) for agentic behavior[22][23].
•	Installation: Claude Code can be installed via npm/Bun (bun install -g @anthropic-ai/claude-code) or a provided shell script[24][25]. It requires an Anthropic account and API key or Claude Cloud subscription (Claude Code is a paid service at the time of writing[26]). The VS Code extension (“Claude Code for VS Code”) is available, but note that it requires the Claude Code CLI to be running locally[27]. In VS Code, the extension provides a chat panel where you can use the same slash commands; for instance, you can type /clear or a custom /test command within the chat to control Claude[3][13].
Sources: Claude Code official docs[20][10], builder.io tips[3][13], Anthropic release notes on slash commands[22][23].
Google Gemini CLI
Overview: Gemini CLI is Google’s open-source AI agent for coding that runs in the terminal[28]. It provides slash commands (/command) for meta-operations and supports custom extension commands via TOML files. Gemini CLI shares technology with Google’s Gemini Code Assist (the IDE plugin), meaning many CLI features (tools, slash commands, etc.) are accessible in VS Code as well[29][30].
•	Built-in Slash Commands: Gemini CLI includes numerous slash commands for session management, configuration, and tooling. For example:
•	/help (or /?): show help menu with available commands[31].
•	/clear: clear the terminal chat history (also accessible via Ctrl+L)[32].
•	/compress: summarize and compact the conversation to conserve tokens[33].
•	/chat: manage saved conversation checkpoints with subcommands – save <tag> (save session state), resume <tag> (resume a saved state), list (list saved sessions), delete <tag> (remove a saved state), and share <file> (export conversation to Markdown/JSON)[34][35]. This is useful for branching or pausing work.
•	/memory: inspect or modify the model’s context memory loaded from GEMINI.md files[36][37]. Subcommands: add <text> (append to memory), show (display current memory), refresh (reload all GEMINI.md context files)[38][39].
•	/mcp: list or configure connected MCP (Model Context Protocol) servers and tools[40]. You can toggle showing tool descriptions (/mcp desc/nodesc) or view tool schemas[41]. (Pressing Ctrl+T also toggles tool description display[42].)
•	/tools: list currently available tools (such as file read/write, web search, etc.)[43]. Use /tools desc to show detailed descriptions of each tool[44].
•	/stats: show session statistics (token usage, cache hits, etc.)[45].
•	/bug: quickly file a GitHub issue in the Gemini CLI repo (the text after /bug becomes the issue title)[46].
•	/directory (alias /dir): manage additional project directories. You can add directories to the workspace (/dir add <path>) or show included dirs (/dir show)[47][48].
•	/copy: copy the last AI output to clipboard (requires xclip/pbcopy tool on your OS)[49].
•	/editor: open an interactive editor interface for crafting a prompt (and /edit is an alias to open the editor)[50][51].
•	/theme: open a theme picker to change the CLI color theme[52].
•	/auth: switch authentication method (e.g. swap between Google OAuth vs API key)[53].
•	/about: display version info and environment details[54].
•	/privacy: review or adjust privacy settings (data collection consent)[55].
•	/quit (or /exit): exit the Gemini CLI session[56].
•	/vim: toggle Vim mode for the CLI input (when on, the input field behaves like a Vim editor with NORMAL/INSERT modes)[57][58].
•	/init: auto-generate a GEMINI.md context file for your project by analyzing the repository (helps set up project-specific context quickly)[59].
These slash commands let you control the AI agent and environment without leaving the chat interface[60]. In the VS Code Gemini Code Assist chat, a subset of these are available – notably /memory, /stats, /tools, /mcp – to perform the same functions from inside the IDE[30][61].
•	Custom Commands (Extensions): Gemini CLI supports custom slash commands defined as TOML files. Custom commands can be global (~/.gemini/commands/) or project-specific (<repo>/.gemini/commands/)[62]. The command name is derived from the file path: for instance, a file ~/.gemini/commands/deploy.toml defines /deploy, while a nested file <project>/.gemini/commands/git/commit.toml defines /git:commit (using a namespace git:)[63]. In the TOML definition, you specify at minimum a prompt (the text prompt to execute) and optionally a description (shown in /help)[64][65]. You can also leverage argument placeholders: using the special token in your prompt will inject the user’s arguments. If appears outside of a shell command, the raw text is inserted; if inside a shell command (within a !{...} block), the arguments are shell-escaped for safety[66][67]. This allows building powerful custom workflows. Example: a custom grep-code.toml could define a command that greps the codebase for a given pattern, using ` in a shell block to safely include the pattern[68][69]. Gemini CLI will prompt for confirmation before executing any shell commands defined in custom prompts to ensure safety[69]. Custom commands are loaded automatically on CLI startup. You can type/` and press <kbd>Tab</kbd> to see all commands, including your custom ones. This system is analogous to Claude Code’s custom commands but uses TOML (with support for inline shell operations and context injections).
•	Installation: Gemini CLI can be installed via npm (npm install -g @google/gemini-cli) or Homebrew (brew install gemini-cli), or run without install using npx[70]. It requires Node.js ≥ 20 and supports macOS, Linux, Windows[71]. On first run, you’ll authenticate with either a Google account (free access to Gemini 2.5 Pro) or an API key (Google Cloud Vertex or AI Studio)[72][73]. In VS Code, Gemini Code Assist (Insiders build) integrates Gemini CLI’s agent: you can open the chat panel and use slash commands like /memory or /tools directly in the IDE to manage the assistant’s behavior[74][75].
Sources: Gemini CLI docs[32][31][43], Google Developers site[61], Google Cloud blog[28].
aider CLI
Overview: aider is an open-source AI coding assistant CLI (created by Aider-AI) that pairs with GPT models to modify and generate code in your local project. It runs in the terminal and uses a chat interface for interactions. Aider supports numerous in-chat slash commands (all beginning with /) to manage files, modes, and the session[50]. It focuses on tightly integrating with Git: it tracks file changes and can commit them incrementally.
•	Built-in Slash Commands: Aider has a rich set of commands to control its behavior and your project. File management & context:
•	/add – Add one or more files to the chat session (so the AI can read/edit them)[76]. Files can also be specified when launching aider, but /add lets you include more on the fly.
•	/drop – Remove a file from the chat context (to save token space)[77]. Similarly, /read-only toggles a file as read-only reference (AI can read but not modify it)[78].
•	/ls – List all files known to aider, marking which are currently in the chat context vs. just tracked in Git[79].
•	/diff – Show the diff of changes in the working directory since the last AI message (i.e., what edits aider just made)[80]. This helps you review AI changes before accepting.
•	/commit – Commit any out-of-chat changes in the repo (with optional message)[81]. (Aider auto-commits changes it applies, but this is for external edits.)
•	/undo – Undo the last Git commit made by aider (revert the commit)[82].
Modes and queries:
- /code – Switch to “code mode” (the default), or if followed by a prompt, ask the AI to make code changes according to that prompt[83]. Without arguments, entering /code toggles into code-editing mode (where subsequent messages assume you want changes).
- /ask – Switch to Q&A mode (ask questions about the code base without editing). With a prompt, it asks the question directly[84]. This is useful for getting explanations or design advice instead of edits.
- /context – Enter “context mode” to view surrounding code context for a given location[85]. You can supply a prompt (like a search query) or just enter /context to toggle mode.
- /architect – Enter architect mode, which uses a secondary “architect” model to discuss higher-level changes before editing (aider can use two models: a main coder model and an architect model)[76]. This command switches to that multi-model workflow.
- /weak-model and /model – Change the AI models in use. /model switches the Main Model (primary coding model) and /weak-model switches the secondary model (used for certain reasoning tasks)[86][87]. For instance, /model gpt-4 could swap in GPT-4 if you have access.
- /chat-mode – Toggle between predefined chat modes (code, ask, etc.) if needed[88].
- /multiline-mode – Toggle how the Enter key works: in multiline mode, Enter inserts a newline and you use Meta+Enter (or similar) to send; by default, Enter sends and Meta+Enter adds a newline[89][90]. This is helpful for crafting longer prompts.
Utilities & tools:
- /copy – Copy the last assistant message to clipboard[80].
- /copy-context – Copy the entire current conversation (system/user/assistant messages) as Markdown text[80], which can be useful for sharing the session or pasting into a web UI.
- /paste – Paste image or text from clipboard into the chat (for example, paste a screenshot or code snippet)[91].
- /lint – Run a linter on the files in chat (or all changed files) and have the AI fix any issues it finds[92]. This automates linting/formatting corrections.
- /test – Run tests (or any shell command) and capture output only if the exit code is non-zero (i.e. test failures). This is useful to have aider run your test suite and only show failing output, which the AI can then attempt to fix[93].
- /run – Run an arbitrary shell command and optionally include its output into the chat. This is aliased by the shorthand ! at the start of a message[94]. By default, output is not injected into the conversation unless you specifically allow it.
- /map – Generate a “repository map” – an overview of the project structure (files and possibly summaries)[95]. Aider auto-generates a repo map for context; this command prints it out. /map-refresh forces an update of that map[95].
- /settings – Show current configuration settings (like which models are being used, token limits, etc.)[96].
- /tokens – Report token usage statistics for the current session[93].
- /report – Open a GitHub issue in the aider repo to report a problem (prefills with relevant info)[97].
Session management:
- /clear – Clear the chat history (start a new session, but unlike Claude’s /clear, aider retains file context; it just clears conversation)[98].
- /reset – Drop all files from the session and clear history[99], essentially resetting aider completely for a new project.
- /exit or /quit – Cleanly exit the aider application[100][78].
As seen, aider’s commands cover adding/removing files, switching modes, getting info, and integrating with git and shell – allowing fine-grained control of the AI coding workflow[76][94]. These commands are invoked by simply typing them into the chat prompt. For quick access, you can press the up arrow to scroll through past commands or Ctrl+R to search your command history[101].
•	Custom Commands: Unlike Claude or Gemini, aider currently does not support user-defined slash commands via config files (as of 2025). All commands are built-in. Users have requested template or macro features[102][103], but presently you cannot add new slash commands to aider except by modifying its source. The Continue.dev extension or other tools may allow custom prompts, but aider’s functionality for slash commands is fixed. (There is a feature request for “prompt templates” or custom commands in aider’s GitHub issues[102], but it’s not implemented yet.) However, aider does allow some customization via a config file (for model settings, etc.), and complex multi-step operations can be scripted by writing a sequence of commands to a file and using /load to execute them[92].
•	Installation: aider is a Python package. You can install it with pip (python3 -m pip install aider-chat) or use the provided installer (pip install aider-install which handles venv isolation)[104]. After installation, run aider <files> in a Git repository to start a session (aider will require an OpenAI or other LLM API key configured)[105]. In VS Code, aider doesn’t have an official extension, but you can use the terminal or integrate via editor plugins (some community integrations exist). Aider’s CLI works best alongside your editor: you edit or select code and ask aider to modify it via the terminal chat. (Some users use aider in VS Code’s terminal or use the Continue extension to similar effect.)
Sources: Official aider documentation[76][94], aider usage docs[50][86].
GitHub CLI (gh)
Overview: The GitHub CLI (gh) is a command-line tool to interact with GitHub from your terminal. While not an “AI assistant,” it’s included here for completeness. It provides subcommands (not slash commands) to manage GitHub repos, issues, PRs, and more. Custom commands are supported via aliases and extensions.
•	Built-in Commands: gh is structured as gh <command> <subcommand> [flags]. Key command groups include:
•	Issues: gh issue list (list issues), gh issue view <number> (view details), gh issue create (open a new issue with prompts or flags), gh issue close[106].
•	Pull Requests: gh pr list, gh pr view <number>, gh pr checkout <number> (check out the PR branch locally), gh pr create (create a PR from your current branch), gh pr merge[107][108].
•	Repositories: gh repo clone <owner/repo> (clone a repo), gh repo create <name> (create a new repo), gh repo fork <repo> (fork a repository), gh repo view (open repo page)[109].
•	Gists: gh gist list, gh gist view <id>, gh gist create <file> (create a new gist from a file).
•	Actions (CI/CD): gh run list (list GitHub Actions runs), gh run watch (watch a running workflow), gh run rerun (re-run a failed workflow)[110][111]. The gh workflow command manages workflow files (enable/disable/list workflows)[112].
•	Extensions: gh extension install <owner/repo> (install a CLI extension), gh extension list, gh extension upgrade, etc. (See Custom Commands below)[113].
•	General: gh auth login (authenticate to GitHub), gh auth status (see auth info), gh browse (open the current repo in web browser), gh search repos/users/issues (search GitHub), gh alias (manage aliases), gh status (overall status like notifications).
•	Help & Info: gh --help or gh <command> --help to see usage; gh --version to show version[114].
Essentially, any GitHub operation can be done: creating issues/PRs, viewing and editing releases (gh release create/edit), managing collaborators (gh repo add-collaborator), checking notifications (gh notification), etc. The CLI mirrors much of the GitHub API. For brevity, the above are major examples. (For a full list, see the official docs or run gh help.)
•	Custom Commands: GitHub CLI allows extending and customizing commands in two ways:
1. Aliases: You can define shortcuts for commands using gh alias set <name> '<gh command sequence>'. For example, gh alias set co 'pr checkout' creates a new command gh co that checks out a pull request[115]. Aliases can compose multiple commands with && or ; as well. Aliases are stored in ~/.config/gh/aliases.yml and can be listed with gh alias list[116]. This lets you create custom “subcommands” that expand to longer sequences. (Example: gh alias set issue-details 'issue view -R $1 $2 -c' to view an issue with comments for a given repo and issue number.)[116].
2. Extensions: The CLI supports plugins called extensions. An extension is basically an external command that gh can delegate to. Any executable on your PATH named gh-<extname> will be invokable as gh <extname>. GitHub has a registry of community extensions (repos tagged with gh-extension)[117]. For example, an extension repo named gh-org/gh-user-stats providing an executable gh-user-stats would allow gh user-stats command. You install extensions via gh extension install <repo>[113], and manage them with gh extension list, gh extension update, etc. These effectively add new top-level commands that weren’t part of core. They cannot override built-in commands (if name conflicts, use gh extension exec <name> to force the extension)[118]. Many extensions exist, e.g., gh browse was originally an extension before becoming core, and others provide functionalities like opening a PR in your browser, managing issue templates, etc.[119][120].
Note: The CLI does not have “in-chat” commands (since it’s not a chat interface). The customizations are via alias and extension scripts.
•	Installation: GitHub CLI (gh) can be installed on all platforms. On macOS: brew install gh. On Ubuntu/Debian: sudo apt install gh (via the official package). Windows: via Scoop, Winget or the MSI installer. You can also download binaries from the GitHub releases. After install, run gh auth login to authenticate. No VS Code extension is needed for GitHub CLI, though VS Code’s built-in GitHub integrations or the separate “GitHub CLI Extension” can integrate its usage.
•	Usage Example: Run gh issue create to open an issue in the current repo – it will prompt for title and body in an editor or via flags[121]. Use gh pr checkout 42 to fetch and switch to PR #42’s branch[122]. Or define an alias: gh alias set redo 'pr checkout $1 && gh pr comment $1 -b \"Rebased 📦\"' to quickly check out a PR and comment on it. The CLI’s flexibility with scripting and aliases makes it a powerful tool for developers.
Sources: GitHub CLI cheat sheet[109][107], official manual[119][123].
VS Code Extensions (AI Assistants)
Modern IDE extensions bring these AI assistants into the editor. In Visual Studio Code, several extensions provide in-editor chat and commands, often mirroring the CLI tools. Below we detail a few notable ones and their in-chat commands or special features:
GitHub Copilot Chat (VS Code)
GitHub Copilot Chat is an extension (part of Copilot for Business/Enterprise) that opens an interactive chat panel in VS Code where you can converse with an AI (powered by OpenAI GPT-4). It supports slash commands in the chat input to quickly invoke common actions[124][125].
•	Slash Commands in Copilot Chat: To use one, you type / in the chat box and select a command. Common commands include:
•	/explain – Explain code. If you have code selected in the editor (or active file), Copilot will describe what it does[125]. This is great for understanding unfamiliar code.
•	/fix – Fix code. Use this when you’ve highlighted code with an error/bug; Copilot will suggest a fix[125].
•	/tests – Generate tests for the selected code (unit tests or relevant test cases)[125].
•	/fixTestFailure – If a test is failing, Copilot will attempt to find the cause and fix the code or test[126].
•	/help – Show Copilot help and tips for using the chat[126].
•	/clear – Clear the current conversation context (start a new chat)[127].
•	/new – (In some contexts) create a new conversation or even a new project scaffold, depending on environment[126]. (In the GitHub web version, /new starts a new chat; in VS Code it may be less used since you can just clear or open a new panel.)
These slash commands basically pre-fill the user prompt with particular instructions so you don’t have to type them. For example, /explain is equivalent to asking “Explain the selected code.” Using slash commands helps set the context or intent (“refactor”, “document”, etc.) without manual prompt engineering[128][129]. Note: In Visual Studio (the JetBrains or VS IDE), the set of commands may differ slightly (e.g., /iterate, etc.), but the concept is similar[130].
•	Other Features: Copilot Chat also supports mentions (@-mentioning specific files or GitHub issues to include them in context)[131] and chat variables (like referencing the current file name or language) to tailor responses. It does not allow arbitrary custom slash commands (you can’t define new ones), but GitHub continuously adds more.
•	Installation: Copilot Chat requires a Copilot subscription and enabling the VS Code Copilot Chat extension (GitHub Copilot Chat – Insiders at time of writing). Once installed, a “Copilot Chat” pane appears. You log in with your GitHub account (which must have access). Then you can start a conversation or use slash commands.
•	Usage Example: Highlight a block of code in the editor, open Copilot Chat, and type /explain – the AI will respond with an explanation of that code[125]. Or if you see an error, type /fix and Copilot will suggest a patch. These quick commands integrate with VS Code’s context (selection, active file, etc.) automatically, making the chat context-aware of your code.
Sources: GitHub Docs (Copilot Chat slash commands)[125][132], MS devblog[129].
Continue (open-source VS Code extension)
Continue.dev is an open-source VS Code extension that acts as an “AI junior developer”. It provides a chat interface similar to Copilot Chat and supports slash commands, including custom commands that users can program. Continue is built to be extensible: you can define new slash commands in JavaScript/TypeScript as part of its config[133][134].
•	Built-in Commands: Continue’s default slash commands include tasks like:
•	/ask – Ask a question about the code without making changes (akin to a Q&A mode).
•	/edit – Ask the AI to edit the code (the extension will apply the changes to your files).
•	/rewrite – Instruct the AI to rewrite or refactor the selected code.
•	/create-test – Generate tests for the selected function or file.
•	/explain – Explain the selected code (similar to Copilot’s /explain).
These are representative – the actual list can be seen by typing / in the Continue chat input. The extension may also have commands like /run-tests or others depending on the version. Each command biases the AI toward a certain action (explain vs. modify vs. add new code).
•	Custom Slash Commands: A standout feature of Continue is that you can create your own slash commands by editing its configuration (continue.config.js or a similar file). For example, you could define a /commit_message command that composes a commit message. The docs show that you can push an object to config.slashCommands with a name, description, and a run function that implements the command[135][136]. This run function has access to Continue’s SDK, so it can gather context (like a git diff) and then stream AI output. In the StackOverflow example above, a custom /commit_message_any_changes command was created to read the git diff and ask the LLM for a commit message[137][138]. By extending it to accept an argument (like an issue ID), one could include that ID in the commit message. Continue’s architecture allows passing arguments after the command name (the question was how to capture them in the run function – the solution involves parsing the args parameter once the method signature is adjusted). In summary, Continue enables power users to script their own IDE-level AI workflows – for instance, a /deploy command could run tests, build the project, and ask the AI to summarize deployment steps. Writing a custom command requires knowledge of JS/TS and the Continue API, but it’s a unique capability among VS Code AI assistants.
•	Usage & Installation: Install Continue from the VS Code Marketplace (“Continue – Open Source Code AI”). After installing, you’ll configure an LLM API (OpenAI, etc.) in its settings. In the chat sidebar, you can type prompts or /commands. For example, type /rewrite function to use async/await while a function is selected – Continue will rewrite it accordingly. Or create a custom /todo command that scans your code for TODO comments. Continue runs the model either locally (if you have one) or via API, depending on setup.
Sources: Continue documentation[139], Continue StackOverflow example[136][137].
Google Gemini Code Assist (VS Code)
Gemini Code Assist is Google’s AI coding helper integrated into VS Code (part of Google Cloud Code). It has a chat UI that can operate in two modes: standard completion and agentic mode (which uses Gemini CLI’s capabilities). In agent mode, you can use Gemini CLI slash commands within VS Code[74].
•	Commands in Chat: As mentioned earlier, Gemini Code Assist’s chat supports a subset of the Gemini CLI slash commands for convenience: e.g. /memory, /stats, /tools, /mcp can be invoked in the chat panel[74][75]. This means you can, say, type /memory show in the VS Code chat to see what project instructions (from GEMINI.md) are in effect, without leaving VS Code. Or use /tools to list what tools (Google Search, terminal, etc.) are available to the agent[140]. The agent mode in VS Code essentially mirrors the CLI’s abilities (like doing multi-step plans, using web search if you allow, etc.), so having these slash commands helps manage it. Additionally, Gemini Code Assist supports a “YOLO mode” toggle (likely via a slash command or button) which lets the AI run more freely with fewer confirmations[141].
•	How it works: You enable agent mode (for users in the trusted testers program or via an Insiders build). Then you can chat like “Fix the bug in this file” and the AI may plan a multi-step fix (like identify bug, edit file, run tests). If it needs web info or file context, it might use integrated tools. The slash commands allow you to intervene or get info (similar to how you’d use them in CLI). Custom commands from the CLI (if any .gemini/commands are defined) might not directly show up in VS Code UI, but core ones do.
•	Installation: Gemini Code Assist is part of Google Cloud’s IDE tools. Individuals can access a free tier (as noted, Gemini 2.5 Pro with large context) by logging in with Google in the extension[142]. The VS Code extension is typically installed from the VS Code Marketplace (“Google Gemini Code Assist”). After linking your Google account or API key, you can open the chat sidebar. A prompt like “/mcp” will list any connected MCP servers (for example if you connected a GitHub integration for the CLI, it would show here too)[140].
Sources: Google Dev documentation[61], Google blog[143].
Claude AI integrations in VS Code
There are community-built VS Code extensions that integrate Claude (Anthropic’s model) into the editor. For instance, “Claude Code Assistant for VSCode” is an unofficial plugin[144] that uses Claude’s API (or Claude Code CLI) to provide chat and completion. The exact commands depend on the extension: many simply provide a chat box without special slash commands. However, if the extension is paired with Claude Code (the CLI), then all the Claude Code slash commands (described earlier: /clear, /test, etc.) are available to use in the chat. Essentially, the VS Code panel would just be a front-end to the Claude Code session running in the background[145]. In that case, you can use custom commands you defined in .claude/commands, perform /compact, etc., just as you would in the terminal.
Other Claude integrations might include using the Claude API for completions (like an alternative to Copilot). Those typically don’t have slash commands, they operate more like autocompletion. One could also use the Continue extension with Claude as the backend model (Continue supports Anthropic models). In that scenario, the slash commands are those of Continue, but powered by Claude’s intelligence.
Summary: In VS Code, GitHub Copilot Chat and Google’s Gemini Code Assist offer built-in slash commands to streamline tasks (clear, explain, test, etc.), while Continue allows creating your own commands. Claude’s official presence in VS Code relies on the Claude Code CLI, which brings its powerful slash commands into the editor environment. Each of these integrations aims to make it easier to “tell” the AI what you want (in natural language or via shortcuts) without always writing lengthy prompts.
Sources: VS Code Copilot docs[125], Google dev guide[74], Continue forum[139], Anthropic Claude Code marketplace listing[146].
________________________________________
[1] [4] [5] [9] [10] [11] [14] [15] [16] [17] [18] [19] [20] [21] Slash Commands in the SDK - Claude Docs
https://docs.claude.com/en/docs/claude-code/sdk/sdk-slash-commands
[2] [3] [6] [7] [8] [12] [13] [26] How I use Claude Code (+ my best tips)
https://www.builder.io/blog/claude-code
[22] [23] Claude Code can invoke your custom slash commands : r/ClaudeAI
https://www.reddit.com/r/ClaudeAI/comments/1noyvmq/claude_code_can_invoke_your_custom_slash_commands/
[24] [25] agent-workflows.md
https://github.com/verlyn13/journal/blob/96d14a3153f3ee5901a44dc70aaceb29b404633e/docs/workflows/agent-workflows.md
[27] [145] [146] Claude Code for VS Code - Visual Studio Marketplace
https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
[28] [142] [143] Google announces Gemini CLI: your open-source AI agent
https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/
[29] [30] [61] [74] [75] [140] [141] Gemini CLI  |  Gemini Code Assist  |  Google for Developers
https://developers.google.com/gemini-code-assist/docs/gemini-cli
[31] [32] [33] [34] [35] [36] [37] [38] [39] [40] [41] [42] [43] [44] [45] [46] [47] [48] [49] [52] [53] [54] [55] [56] [57] [58] [59] [60] [62] [63] [64] [65] [66] [67] [68] [69] CLI Commands | gemini-cli
https://google-gemini.github.io/gemini-cli/docs/cli/commands.html
[50] [51] [76] [77] [78] [79] [80] [81] [82] [83] [84] [85] [86] [87] [88] [89] [90] [91] [92] [93] [94] [95] [96] [97] [98] [99] [100] [101] In-chat commands | aider
https://aider.chat/docs/usage/commands.html
[70] [71] [72] [73] Gemini CLI | gemini-cli
https://google-gemini.github.io/gemini-cli/
[102] [103] Feature request - templates for aider · Issue #1815 · Aider-AI/aider · GitHub
https://github.com/Aider-AI/aider/issues/1815
[104] Installation - Aider
https://aider.chat/docs/install.html
[105] How to Create Custom Slash Commands in Amp CLI - YouTube
https://www.youtube.com/watch?v=_wKToRRN680
[106] [107] [108] [109] [114] build5nines.com
https://build5nines.com/wp-content/uploads/2020/04/GitHub-CLI-Cheat-Sheet-Build5Nines.pdf
[110] [111] [112] [113] [116] [117] [118] [119] [120] [123] GitHub CLI | Take GitHub to the command line
https://cli.github.com/manual/gh_extension
[115] GitHub CLI brings GitHub to your terminal | by Ravi | Analytics Vidhya
https://medium.com/analytics-vidhya/github-cli-brings-github-to-your-terminal-809cea627d62
[121] GitHub CLI — GitHub From The Command Line | by Nate Ebel
https://medium.com/goobar/github-cli-github-from-the-command-line-bfdbaa3e1a94
[122] GitHub CLI: create and manage PRs from the command line
https://eszter.space/gh-cli/
[124] [125] [126] [127] [131] [132] GitHub Copilot Chat cheat sheet - GitHub Docs
https://docs.github.com/en/copilot/reference/cheat-sheet
[128] Customize chat responses - Visual Studio (Windows) | Microsoft Learn
https://learn.microsoft.com/en-us/visualstudio/ide/copilot-chat-context?view=vs-2022
[129] [130] Code Faster and Better with GitHub Copilot's New Features: Slash ...
https://devblogs.microsoft.com/visualstudio/copilot-chat-slash-commands-and-context-variables/
[133] [135] [136] [137] [138] [139] How to Pass Arguments to Custom Slash Commands in Continue.dev
https://stackoverflow.com/questions/79324479/how-to-pass-arguments-to-custom-slash-commands-in-continue-dev
[134] [Slash command `/onboard`] [macOS] `/onboard` slash ... - GitHub
https://github.com/continuedev/continue/issues/4151
[144] Claude Code Assistant for VSCode - Visual Studio Marketplace
https://marketplace.visualstudio.com/items?itemName=codeflow-studio.claude-code-extension
