# LeetCode Daily Companion

## 1. Project overview

Build a lightweight, keyboard-driven LeetCode Daily Challenge
application that runs locally on Linux.

The application should feel like an existing shell command (for example,
a personal `movies` command), rather than a traditional desktop
application. It should work consistently on KDE Plasma and Hyprland,
with Hyprland keybindings as a first-class use case.

The primary goal is to make the daily problem easy to discover and start
solving:

-   Run one command to view today's challenge.
-   See the essential metadata without opening a browser.
-   Run `attempt` to open the full problem statement alongside a local
    coding workspace in VS Code.
-   Execute sample and custom test cases locally.
-   Keep a local history of challenges and attempts.

The application should not require a permanently running background
daemon.

## 2. Expected user experience

### Daily overview

Running:

``` bash
lc
```

opens a compact interactive terminal UI showing:

-   Challenge date
-   Tags / topic names
-   Question name
-   Question ID
-   Completion status (where available from the authenticated account)
-   Difficulty

The interface should provide commands such as:

-   `attempt` --- switch to the detailed problem view and open the
    coding workspace.
-   `refresh` --- fetch the latest daily challenge.
-   `history` --- view previously cached or attempted challenges.
-   `quit` --- exit the application.

The challenge should be cached locally so repeatedly opening the
overview does not repeatedly call LeetCode.

### Attempt workflow

Running `attempt` from the overview should:

1.  Load the full problem details.
2.  Show the problem statement in a readable, formatted view in the
    existing terminal UI.
3.  Create or locate that day's problem workspace.
4.  Generate the language-specific starter file using LeetCode's
    supplied code snippet.
5.  Generate sample test scaffolding where the sample input/output
    format can be handled safely.
6.  Launch VS Code at the workspace directory.

The terminal UI remains the problem viewer. VS Code is a separate window
for editing. The window manager is responsible for arranging the windows
side by side.

### Local testing

The initial implementation should support Python.

A generated workspace could look like:

``` text
~/leetcode/
└── problems/
    └── 2026-11-21-two-sum/
        ├── README.md
        ├── solution.py
        └── test_solution.py
```

`README.md` contains the problem statement, constraints, examples, tags
and source link.

`solution.py` contains LeetCode's Python starter snippet.

`test_solution.py` imports `Solution`, calls the expected method with
sample inputs, and compares results with expected outputs. Pytest is a
suitable initial test runner.

Passing local sample tests does not guarantee acceptance by LeetCode:
hidden judge tests are not publicly available through the ordinary
problem query.

## 3. Proposed command interface

  -----------------------------------------------------------------------
  Command                             Behaviour
  ----------------------------------- -----------------------------------
  `lc`                                Open today's challenge overview

  `lc refresh`                        Fetch and cache the current daily
                                      challenge

  `lc attempt`                        Open the detailed challenge view
                                      and VS Code workspace

  `lc history`                        Show locally stored challenge
                                      history

  `lc test`                           Run tests for the current or
                                      selected workspace

  `lc config`                         View or edit application
                                      configuration
  -----------------------------------------------------------------------

The interactive UI should also accept commands such as `attempt` and
`refresh`.

## 4. Why this should be a Python CLI/TUI

This is not fundamentally a KDE widget or a Hyprland extension. It is a
local command-line application with an interactive terminal user
interface.

Recommended technologies:

-   **Python** --- application language and integration logic.
-   **Typer** --- parse commands such as `lc refresh` and `lc attempt`.
-   **Textual** --- build the interactive terminal interface.
-   **SQLite** --- cache challenge metadata and maintain local history.
-   **LeetCode GraphQL** --- retrieve daily challenge and problem
    details.
-   **pytest** --- run local Python tests.
-   **VS Code CLI (`code`)** --- open the generated workspace.

Reasons for this choice:

1.  **Desktop independence:** a terminal application works on both KDE
    Plasma and Hyprland.
2.  **Keyboard-first workflow:** Textual supports keyboard navigation
    and command-driven interfaces.
3.  **Simple launch model:** the executable can live in `~/.local/bin`,
    just like an existing shell script.
4.  **No daemon required:** each invocation starts a process, performs
    its task, and exits; the interactive TUI stays alive only while
    being used.
5.  **Easy to extend:** API access, storage, workspace generation, UI
    and window-manager integration can be kept separate.

Typer documentation: https://typer.tiangolo.com/

Textual documentation: https://textual.textualize.io/

## 5. Proposed filesystem layout

Keep the executable separate from the application source and user data.

``` text
~/.local/bin/
└── lc                         # Executable entry point

~/.local/share/leetcode/
├── app/
│   ├── main.py
│   ├── commands/
│   │   ├── daily.py
│   │   ├── attempt.py
│   │   └── history.py
│   ├── services/
│   │   ├── leetcode.py
│   │   ├── workspace.py
│   │   └── runner.py
│   ├── storage/
│   │   └── database.py
│   └── ui/
│       ├── dashboard.py
│       └── problem.py
├── data/
│   └── leetcode.db
└── config.toml

~/leetcode/
└── problems/                  # User's generated coding workspaces
```

The `~/.local/bin/lc` executable should be a small Python entry point
that imports and invokes the application. Ensure `~/.local/bin` is on
`$PATH`.

## 6. Fetching the exact LeetCode function signature

Do not infer the method name, parameters or return type from the problem
title.

LeetCode's GraphQL `question` query exposes:

-   `codeSnippets` --- language-specific starter code.
-   `metaData` --- problem metadata, including parameter and return-type
    information where supplied.
-   `content` --- problem statement and examples.
-   `exampleTestcases` --- published sample input data.
-   `questionFrontendId`, `title`, `titleSlug` and `difficulty` ---
    identifying information.

Example query for Two Sum:

``` graphql
query questionData {
  question(titleSlug: "two-sum") {
    questionId
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    exampleTestcases
    metaData
    codeSnippets {
      lang
      langSlug
      code
    }
  }
}
```

The application should select the snippet whose `langSlug` is `python3`
and use its `code` as the initial `solution.py`.

For example, a returned snippet may contain:

``` python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
```

Another problem will return its own class and method signature. The
application should preserve that supplied starter code rather than
trying to construct a signature from scratch.

### Function signature versus test input format

These are separate concerns:

-   The **starter snippet** tells us the class name, method name and
    function signature.
-   **Problem metadata** can provide structured parameter and
    return-type information.
-   **Example testcases** provide published sample input data.
-   The **problem statement** explains how those inputs and outputs
    should be interpreted.

For typical Python LeetCode problems, the judge invokes the method
directly. A local test runner can do the same:

``` python
from solution import Solution

solution = Solution()
actual = solution.twoSum([2, 7, 11, 15], 9)
assert actual == [0, 1]
```

Do not assume all problems can use this simple test structure. Linked
lists, binary trees, nested structures and other serialized inputs need
appropriate adapters. Start with common problem types and expand the
runner deliberately.

The sample test parser should not use unrestricted `eval()` on
API-provided text. Use safe parsing and explicit adapters.



## 7. Required LeetCode GraphQL requests

The following `curl` commands document the concrete GraphQL requests used by the application. Keep these queries in the project documentation as the reference contract for the initial implementation.

### 7.1 Daily problem info — TUI overview (`lc`)

**Purpose:** Used by the TUI when the user runs `lc` to display the compact daily challenge overview.

It retrieves the challenge date, account status exposed by the response, problem link, question ID, title, slug, difficulty and acceptance rate.

```bash
curl --request POST \
  --url https://leetcode.com/graphql \
  --header 'Content-Type: application/json' \
  --header 'Referer: https://leetcode.com' \
  --data '{"query":"query dailyChallenge { activeDailyCodingChallengeQuestion { date userStatus link question { questionFrontendId title titleSlug difficulty acRate } } }","variables":""}'
```

### 7.2 Detailed daily problem — TUI problem view

**Purpose:** Used when the user enters `attempt` and the TUI needs to show the full problem statement in a readable format.

It retrieves the problem description, examples, topic tags and identifying information.

```bash
curl --request POST \
  --url https://leetcode.com/graphql \
  --header 'Content-Type: application/json' \
  --header 'Referer: https://leetcode.com' \
  --data '{"query":"query questionOfToday { activeDailyCodingChallengeQuestion { date link question { questionFrontendId title titleSlug difficulty content exampleTestcases topicTags { name } } } }","variables":""}'
```

### 7.3 Method signature and starter code — workspace generation

**Purpose:** Used by the Python workspace-generation service when opening the challenge in VS Code.

The example below requests the problem identified by the slug `find-subtree-sizes-after-changes`. In the application, replace this hardcoded slug with the `titleSlug` returned by the daily challenge query.

It retrieves `codeSnippets`, including the language-specific starter code, and `metaData`, which can provide structured information about parameters and return types.

```bash
curl --request POST \
  --url https://leetcode.com/graphql \
  --header 'Content-Type: application/json' \
  --header 'Referer: https://leetcode.com' \
  --data '{"query":"query questionData { question(titleSlug: \"find-subtree-sizes-after-changes\") { questionId questionFrontendId title titleSlug difficulty content exampleTestcases metaData codeSnippets { lang langSlug code } } }","variables":""}'
```

**Implementation notes:**

- The first request is for the lightweight daily overview. Avoid fetching the full problem statement until the user asks to attempt the challenge.
- The second request uses the current daily challenge and retrieves its detailed description. The returned `titleSlug` can be used to identify the problem.
- The third request should use that returned `titleSlug`, rather than a fixed problem slug. Select the returned `codeSnippets` entry with `langSlug` equal to `python3` and use its `code` as the initial `solution.py`.
- These are observed LeetCode GraphQL frontend queries, not a guaranteed, officially supported public API. The response schema or access requirements may change.
- `userStatus` should not be treated as proof of completion for an arbitrary username unless the request is made with the appropriate authenticated account context and the returned status has been verified.
- `exampleTestcases` contains published examples; it does not expose hidden judge test cases.

## 8. LeetCode API considerations

The application can use LeetCode's web GraphQL endpoint:

``` text
https://leetcode.com/graphql
```

Useful operations and fields include:

-   `activeDailyCodingChallengeQuestion` for the current daily
    challenge.
-   `question(titleSlug: ...)` for problem details.
-   `codeSnippets` for language-specific starter code.
-   `metaData` for structured problem metadata.
-   `matchedUser` and related profile fields for public profile
    statistics.

These are undocumented frontend APIs, not a stable, officially supported
public API contract. They can change, enforce rate limits or require
authentication for account-specific information.

Completion status must be treated separately from the public challenge
details. The application should only display a definitive account
completion status when it can verify it using authenticated account
data. Otherwise, show an unknown or unavailable state rather than
guessing.

Cache responses and avoid unnecessary repeated requests. Store
credentials securely if authentication becomes necessary; do not
hardcode cookies or tokens in source code.

## 9. KDE Plasma and Hyprland integration

The application should not implement its own window tiling.

It should launch the terminal UI and VS Code. The window manager should
arrange them.

Example Hyprland keybindings (assuming Kitty is installed):

``` ini
# Open daily challenge
bind = SUPER, L, exec, kitty -e lc

# Open attempt workflow directly
bind = SUPER SHIFT, L, exec, kitty -e lc attempt
```

The application can launch VS Code with:

``` bash
code /home/USER/leetcode/problems/2026-11-21-two-sum
```

Hyprland window rules can position the terminal and VS Code. KDE can
launch the same command through a global shortcut, with KWin handling
window placement.

Keep any window-manager-specific behaviour in small adapters or
configuration, not in the core LeetCode service.

## 10. Suggested implementation phases

1.  **CLI foundation:** create the Python project, install the `lc`
    entry point, and implement command parsing.
2.  **Daily challenge retrieval:** query GraphQL, parse the daily
    challenge and cache it in SQLite.
3.  **Overview UI:** build the compact Textual screen with the requested
    fields and commands.
4.  **Problem details:** retrieve and render the full problem statement,
    examples and tags.
5.  **Workspace generation:** select the Python code snippet and create
    the daily workspace.
6.  **Local test runner:** execute sample and custom tests with safe
    parsing, timeouts and clear results.
7.  **Desktop integration:** launch VS Code and configure Hyprland and
    KDE shortcuts/window placement.
8.  **History and reliability:** add local attempt history, cache
    expiry, error handling and API-change resilience.

## 11. Explicit non-goals for the first version

Avoid adding these until the basic workflow is reliable:

-   A permanent background daemon.
-   A native Plasma widget or Hyprland extension.
-   A web frontend or Electron application.
-   Automatic submission of solutions to LeetCode.
-   Hidden-test retrieval or claims of reproducing LeetCode's complete
    judge.
-   Multi-language support before Python is working well.

## 12. Definition of done

The first useful version is complete when:

1.  Running `lc` opens today's challenge overview.
2.  The overview displays tags, question name, question ID, completion
    status and difficulty.
3.  Reopening the application uses cached data when appropriate.
4.  Typing `attempt` shows the full problem in the existing terminal UI.
5.  The application generates the correct Python starter code from
    LeetCode's returned snippet.
6.  VS Code opens the corresponding local workspace.
7.  Published sample tests and user-added tests can be run locally.
8.  The same workflow can be launched from a Hyprland keybinding and
    from KDE Plasma.
9.  The application works without a permanently running service.

------------------------------------------------------------------------

**Overall decision:** Build a local-first Python CLI/TUI application
using Typer and Textual. Keep the executable in `~/.local/bin/lc`,
application code and cache under `~/.local/share/leetcode`, and coding
workspaces under `~/leetcode`. Let KDE Plasma and Hyprland handle
shortcuts and window placement. This gives a clean, reusable workflow
without tying the application to one desktop environment.
