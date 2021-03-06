import discord
import re
import sys

from data import CsvLoader


class BotClient(discord.Client):
    """
    A discord.Client which reads a .csv of possible replies and responds
    accordingly during on_message events.
    """
    def __init__(self, loader = CsvLoader()):
        super().__init__()
        self.loader = loader

    def _add_response(self, content):
        parameter = self._extract_parameter(content)
        output = ('Added `{}` to {}.' if self.loader.add(parameter) else
                'Failed to add `{}` to {}. Check string formatting and '
                'ensure it corresponds to 4 fields to form a proper row.')
        return output.format(parameter, self.loader.hostname)

    def _delete_response(self, content):
        parameter = self._extract_parameter(content)
        return ('Removed index {}.' if self.loader.delete(int(parameter))
                else 'Index {} not found, nothing removed.').format(parameter)

    def _extract_parameter(self, content):
        parameters = re.split(r'\s+', content, 1)
        return parameters[1] if len(parameters) > 1 else None

    def _list_responses(self, content):
        parameter = self._extract_parameter(content)
        if parameter:
            row = self.loader.list(False, int(parameter))
            output = ('```\nIndex: {}\nPattern: {}\nResponse: {}'
                    '\nRequires Mention: {}\nReact Emoji: {}```'
                    .format(parameter, *row[0]) if row else
                    'Row {} not found.'.format(parameter))
        else:
            output = ('Listing all stored responses.\nUse `!list <index>` '
                    'to fully show individual rows.\n```')
            for index, row in enumerate(self.loader.list(True)):
                output += '{}: {} | {} | {} | {}\n'.format(index, *row)
            output += '```'
        return output

    def _load_responses(self, *_args):
        commands = [
            BotCommand(r'^!reload$', self._load_responses),
            BotCommand(r'^!list$|^!list\s+\d*$', self._list_responses),
            BotCommand(r'^!add\s+.+$', self._add_response),
            BotCommand(r'^!delete\s+\d*$', self._delete_response),
        ]
        self.responses = {cmd.pattern.pattern: cmd for cmd in commands}
        for row in self.loader.list():
            reply = self.responses.get(row[0])
            if reply:
                reply.messages.append(row[1])
            else:
                self.responses[row[0]] = BotReply(*row)
        success = 'Loaded responses from {}.'.format(self.loader.hostname)
        print(success)
        return success

    async def on_ready(self, default_id = None):
        print('Logged on as {0}!'.format(self.user))
        bot_user_id = getattr(self.user, 'id', default_id)
        self.mention = re.compile("<@[!&]*{}>".format(bot_user_id))
        self._load_responses()

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.author != self.user:
            for response in self.responses.values():
                if ((not response.require_mention
                        or self.mention.search(message.content))
                        and await response.reply_to(message)):
                    break


class BotReply:
    """Self-contained message logic integrated with regex."""
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

    async def _react_to(self, message):
        if self.react_emoji:
            try:
                await message.add_reaction(self.react_emoji)
            except discord.errors.HTTPException as invalid_emoji:
                self.react_emoji = ''
                print(invalid_emoji)

    async def reply_to(self, message, response = '', skip_regex = False):
        """Sends a Discord message if pattern matches the given message."""
        result = False
        if skip_regex or self.pattern.search(message.content):
            if not response:
                response = self.messages[self.index]
                self._next_message()
            await message.channel.send(response)
            await self._react_to(message)
        return result


class BotCommand(BotReply):
    """Bot command with a callback and privilege level required to activate."""
    def __init__(self, pattern, callback = lambda: None,
                privilege = 'administrator'):
        super().__init__(pattern, '', 0, '')
        self.callback = callback
        self.privilege = privilege

    async def reply_to(self, message):
        if (self.pattern.search(message.content) and getattr(message.channel
                .permissions_for(message.author), self.privilege)):
            await super().reply_to(
                    message, self.callback(message.content), True)


if __name__ == '__main__':
    loader = CsvLoader()
    token = loader.get_token()
    if not token:
        sys.exit("Missing bot token in 'config.ini' | see Your Application "
                "> Bot @ https://discord.com/developers/applications")
    try:
        BotClient(loader).run(token)
    except discord.DiscordException as discord_exception:
        sys.exit('Discord client error: ' + str(discord_exception))
    except OSError as os_error:
        sys.exit('An error occurred when processing a file: ' + str(os_error))
