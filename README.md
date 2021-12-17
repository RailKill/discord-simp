# Discord Simple RegEx Message Bot
This bot will read messages from any channel it is in, search the message for a RegEx pattern defined in the first column of 'replies.csv',
and replies with the second column of 'replies.csv' if a match is found. It was not designed as a public bot, but pull requests to support
this feature and store responses per server are welcomed.


## How to Use
1. Create your Discord bot username by following this guide: https://discordpy.readthedocs.io/en/stable/discord.html
2. Download and install latest version of [Python](https://www.python.org/downloads/).
3. `git clone` this repository or download as zip under the green Code button in this GitHub page and extract it.
4. Open `cmd` and go into repository folder by typing `cd <REPOSITORY_FOLDER_PATH>`
5. Create virtual environment: `python -m venv bot-env`
6. Activate virtual environment: `bot-env\Scripts\activate` on Windows, `bot-env/bin/activate` on Linux.
7. Install dependencies: `pip install -r requirements.txt`
8. Run the bot: `python bot.py` and it will exit, telling you to go get your bot's token in https://discord.com/developers/applications.
9. Edit config.ini so that `token = <YOUR_BOT_TOKEN>`
10. Repeat step #7 and if it prints "Logged in as <YOUR_BOT_USER>!" then it means it is running.

#### Help! I get gcc build errors when installing the multilib or yarl dependencies!
Use `MULTILIB_NO_EXTENSIONS=1 YARL_NO_EXTENSIONS=1 pip install -r -requirements.txt`. This issue occurs when multilib and yarl wheel binaries
are not available for your operating system, so these extra flags will skip the compilation and use their raw Python scripts (slower performance).


## replies.csv Example

| RegEx Pattern | Message to Send | Requires Mention? | React with Emoji |
| - | - | - | - |
| \bfries\b | "there is the thin skinless ones, thick skinless, thic with skin, truffle oil, sour scream fries, fries dip on MCD ice cream cone" | 0 | 🍟 |

![fries](https://user-images.githubusercontent.com/11093103/146556296-c8b6a00b-4a30-491b-ac42-7f11d3a9ebe4.jpg)

**0:** The regular expression pattern to check the incoming message with.

**1:** The message to send on that same channel if the regular expression found a match.

**2:** Boolean value expressed as 0 or 1. If true, only reply if message mentions the bot.

**3:** If not blank, this unicode emoji will be used to react to the matched message.


## Administrator Commands
Type these commands in any text channel the bot is in to execute them. Only works with users having the Administrator role in that channel.

`!reload` - Loads 'replies.csv' without restarting the bot client.
