# Discord Simple RegEx Message Bot [![unittest](https://github.com/RailKill/discord-simp/actions/workflows/ci.yml/badge.svg)](https://github.com/RailKill/discord-simp/actions/workflows/ci.yml)
This bot will read messages from any channel it is in, search the message for a RegEx pattern defined in the first column of 'replies.csv',
and replies with the second column of 'replies.csv' if a match is found. It was not designed as a public bot, but pull requests to support
this feature and store responses per server are welcomed.


## Installation
1. Create your Discord bot user and invite it to your server by following this guide: https://discordpy.readthedocs.io/en/stable/discord.html
2. Download and install latest version of [Python](https://www.python.org/downloads/).
3. `git clone` this repository or download zip *(under the green Code button or from Releases page)* and extract it.
4. Open `cmd` and go into the repository folder by typing `cd <REPOSITORY_FOLDER_PATH>`
5. Create virtual environment: `python -m venv bot-env`
6. Activate virtual environment: `bot-env\Scripts\activate` on Windows, `bot-env/bin/activate` on Linux.
7. Install dependencies: `pip install -r requirements.txt`
8. Run the bot: `python bot.py` which will generate the config.ini file. It will then exit, telling you
   to get your bot's token from https://discord.com/developers/applications.
9. Edit config.ini so that `token = <YOUR_BOT_TOKEN>`
10. Repeat step #8.

&nbsp;
> **Help! I get gcc build errors when installing the multilib or yarl dependencies!**  
> 
> Try `MULTILIB_NO_EXTENSIONS=1 YARL_NO_EXTENSIONS=1 pip install -r -requirements.txt`. This issue occurs when multilib and yarl wheel binaries
are not available for your operating system, so these extra flags will disable the compiled speedups and use the slower Python scripts instead.
<br/>


## replies.csv Example

| RegEx Pattern | Message to Send | Requires Mention? | React with Emoji |
| - | - | - | - |
| \bfries\b | "there is the thin skinless ones, thick skinless, thic with skin, truffle oil, sour scream fries, fries dip on MCD ice cream cone" | 0 | 🍟 |

![fries](https://user-images.githubusercontent.com/11093103/146556296-c8b6a00b-4a30-491b-ac42-7f11d3a9ebe4.jpg)

<br/>


## Administrator Commands
Type these commands in any text channel the bot is in to execute them. Only works with users having the Administrator role in that channel.

- `!list`
  <details>
  <summary>Shows a truncated list of all rows in the .csv file and their indices. The row index is used in add/delete operations.</summary>
  
  ![list](https://user-images.githubusercontent.com/11093103/146659348-98fa2016-dea9-4073-8242-2eddbebc6da9.jpg)
  </details>

- `!list <index>`
  <details>
  <summary>Shows the full detail of the given row index.</summary>
  
  ![list0](https://user-images.githubusercontent.com/11093103/146659473-bb13ea47-7061-415f-a828-6651db9695bd.jpg)
  </details>
  
- `!add <row>`
  <details>
  <summary>Adds a comma-delimited string as a new row into the .csv file.</summary>
  
  ![add](https://user-images.githubusercontent.com/11093103/146659670-18456ce9-c846-4576-98f1-4f60bd31a745.jpg)
  
  The 'row' parameter is entered exactly as how you would type it in the .csv file. In this example, the parameter can be broken
  into 4 parts: `\bsomething\b`, `i'm alive!`, `0` and `<custom emoji>`. It corresponds to the 4 fields shown in the previous **'replies.csv Example'** section.
  </details>

- `!reload`
  <details>
  <summary>Loads 'replies.csv' without restarting the bot client. This should be done after add or delete.</summary>
  
  ![reload](https://user-images.githubusercontent.com/11093103/146659676-8caef86b-b5bf-4a44-811f-90b53ce4176d.jpg)

  After reloading, sending a message that matches the `\bsomething\b` regular expression shown in the previous `!add` example will now trigger the bot's response:
  
  ![saysomething](https://user-images.githubusercontent.com/11093103/146659765-93b20842-ef10-4aad-b61f-79c71a328669.jpg)
  </details>

- `!delete <index>`
  <details>
    <summary>Deletes the given row index from the .csv file.</summary>

    ![delete](https://user-images.githubusercontent.com/11093103/146659768-5ab9cba2-b539-445e-a189-cc1c7a340ba1.jpg)
  </details>
 
 - `!lock <row>`
   <details>
      <summary>Locks bot commands to the given comma-delimited list of permissions, role ids, and user ids.</summary>
      
      By default, bot commands can only be used by users with the administrator permission. It is equivalent to typing `!lock administrator,,` or `!lock reset`.
      [List of permission attributes can be found here](https://discordpy.readthedocs.io/en/stable/api.html#permissions). You can use multiple fields such as
      `!lock "manage_guild,kick_members","123,456",` which will only alow users with permissions levels equal to or greater than manage server + kick, and must
      belong to either role ID 123 or 456. An admin who is not in either role for example, will not be able to use any commands.
   </details>
