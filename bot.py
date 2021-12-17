import configparser
import csv
import discord
import re
import sys


# Default filenames.
CONFIG_FILENAME = 'config.ini'
CSV_FILENAME = 'replies.csv'


class BotClient(discord.Client):
    """A discord.Client which reads a .csv of replies and responds accordingly during on_message events."""
    def _load_responses(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILENAME)
        csv_filename = config.get('csv', 'filename', fallback = CSV_FILENAME)
        try:
            with open(csv_filename, newline='', encoding='utf8') as genius_ideas:
                reader = csv.reader(genius_ideas)
                self.responses = {}
                for row in reader:
                    reply = self.responses.get(row[0])
                    if reply:
                        reply.messages.append(row[1])
                    else:
                        self.responses[row[0]] = BotReply(*row)
        except OSError:
            sys.exit('Unable to load respones from {}'.format(csv_filename))
        print('{} loaded.'.format(csv_filename))
        return csv_filename

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.mention = re.compile("<@[!&]*{}>".format(self.user.id))
        self._load_responses()

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.author != self.user:
            if message.content == '!reload' and message.channel.permissions_for(message.author).administrator:
                await message.channel.send('{} reloaded.'.format(self._load_responses()))
            else:
                for response in self.responses.values():
                    if (not response.require_mention or self.mention.search(message.content)) \
                            and await response.reply_to(message):
                        break


class BotReply:
    """A message integrated with regex."""
    def __init__(self, pattern, message, require_mention, react_emoji):
        self.pattern = re.compile(pattern, re.I)
        self.messages = [message]
        self.require_mention = bool(int(require_mention))
        self.react_emoji = react_emoji
        self.index = 0

    def _next_message(self):
        self.index += 1
        if self.index >= len(self.messages):
            self.index = 0

    async def reply_to(self, message):
        """Automatically perform a regex search on given string and sends a Discord message if there is a match."""
        result = False
        if self.pattern.search(message.content):
            await message.channel.send(self.messages[self.index])
            self._next_message()
            if self.react_emoji:
                await message.add_reaction(self.react_emoji)
        return result


if __name__ == '__main__':
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILENAME):
        config['secret'] = {'token': ''}
        config['csv'] = {'filename:': CSV_FILENAME}
        with open(CONFIG_FILENAME, 'w') as configfile:
            config.write(configfile)

    if not config['secret']['token']:
        sys.exit("Missing bot token in 'config.ini' | "
                "see Your Application > Bot @ https://discord.com/developers/applications")

    try:
        client = BotClient()
        client.run(config['secret']['token'])
    except discord.DiscordException as e:
        sys.exit("Discord client error: " + str(e))
