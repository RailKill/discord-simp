import os
import re
import sys
import warnings
import unittest

from bot import BotClient, BotReply
from unittest.mock import AsyncMock, MagicMock


class NoPrint:
	"""
	Under the 'with NoPrint():' block, any print() output will be hidden.
	This is so that the bot output does not interfere with test case output.
	"""
	def __enter__(self):
		self._original = sys.stdout
		sys.stdout = open(os.devnull, 'w')

	def __exit__(self, exception_type, exception_value, exception_traceback):
		sys.stdout.close()
		sys.stdout = self._original


class TestBotClient(unittest.IsolatedAsyncioTestCase):
	"""Test case for the BotClient class from bot.py"""
	def setUp(self):
		with warnings.catch_warnings():
			warnings.simplefilter('ignore', DeprecationWarning)
			self.client = BotClient()

	async def assert_response(self, message, needs_mention, expect_reply):
		"""Helper assert function for on_message tests."""
		message.author = 'unittest'
		reply_to = AsyncMock()
		self.client.mention = re.compile('<@unittest>')
		self.client.responses = {'boom': AsyncMock(reply_to = reply_to, 
				require_mention = needs_mention)}
		with NoPrint():
			await self.client.on_message(message)
		if expect_reply:
			reply_to.assert_called_with(message)
		else:
			reply_to.assert_not_called()

	def test_load_responses(self):
		with NoPrint():
			self.client._load_responses()
		keys = iter(self.client.responses.keys())
		self.assertEqual(next(keys), r'\bfries\b',
				'Loaded responses 1st key is incorrect.')
		self.assertEqual(next(keys), r'tell.*joke',
				'Loaded responses 2nd key is incorrect.')
		self.assertEqual(len(self.client.responses.keys()), 2,
				'Responses should only contain 2 keys.')

	async def test_on_ready(self):
		self.client._load_responses = MagicMock(name = '_load_responses()')
		with NoPrint():
			await self.client.on_ready(42069)
		self.client._load_responses.assert_called()
		self.assertEqual(self.client.mention.pattern, '<@[!&]*42069>')

	async def test_on_message_respond_general(self):
		# Respond general message.
		await self.assert_response(
				AsyncMock(content = 'badaboom'), False, True)

	async def test_on_message_respond_if_mentioned(self):
		# Respond when require_mention message has a bot mention.
		await self.assert_response(
				AsyncMock(content = 'baboom <@unittest>'), True, True)

	async def test_on_message_ignore_if_not_mentioned(self):
		# Don't respond if require_mention message does not have bot mention.
		await self.assert_response(AsyncMock(content = 'baboom'), True, False)

	async def test_on_message_reload(self):
		# Test on_message event using the '!reload' command.
		message = AsyncMock(content = '!reload', author = 'somebody')
		message.channel.permissions_for = \
				MagicMock(return_value = MagicMock(administrator = True))
		self.client._load_responses = MagicMock(name = '_load_responses()')
		with NoPrint():
			await self.client.on_message(message)
		self.client._load_responses.assert_called()


class TestBotReply(unittest.IsolatedAsyncioTestCase):
	"""Test case for the BotReply class from bot.py"""
	def test_next_message(self):
		reply = BotReply('', 'first', 0, '')
		reply.messages.append('second')
		reply.messages.append('third')
		reply.index = 1
		reply._next_message()
		self.assertEqual(reply.index, 2)
		reply._next_message()
		self.assertEqual(reply.index, 0)

	async def test_reply_to(self):
		message = AsyncMock(content = 'good morning')
		reply = BotReply(r'good\smorning', 'hello', 0, '\U0001F602')
		reply._next_message = MagicMock('_next_message()')
		await reply.reply_to(message)
		message.channel.send.assert_called_with('hello')
		reply._next_message.assert_called()
		message.add_reaction.assert_called_with('\U0001F602')


if __name__ == '__main__':
	unittest.main(verbosity=2)
