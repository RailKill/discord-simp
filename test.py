import os
import re
import sys
import warnings
import unittest

from bot import BotClient, BotReply, BotCommand
from data import CsvLoader
from unittest.mock import patch, AsyncMock, MagicMock


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
			self.client = BotClient(MagicMock())

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

	def test_add_response(self):
		self.client._add_response('!add mabols')
		self.client.loader.add.assert_called()

	def test_delete_response(self):
		self.client._delete_response('!delete 9001')
		self.client.loader.delete.assert_called()

	def test_extract_parameter(self):
		self.assertIsNone(self.client._extract_parameter('single'))
		self.assertEqual(self.client._extract_parameter('1 2nd 30'), '2nd 30')

	def test_list_responses(self):
		expected_list = [['somebody', 'once', '7010', 'me']]
		self.client._extract_parameter = MagicMock(return_value = None)
		self.client.loader.list = MagicMock(return_value = expected_list)
		self.assertIn('0: some', self.client._list_responses('!list'))
		self.client._extract_parameter = MagicMock(return_value = '100')
		self.assertIn('Pattern: some', self.client._list_responses('!list 100'))
		self.client.loader.list = MagicMock(return_value = [])
		self.assertIn('not found', self.client._list_responses('!list 0'))

	def test_load_responses(self):
		self.client.loader.list = MagicMock(return_value = [
			['sigma', 'b', '0', 'l'],
			['je.*', 'bayted', '1', 'x'],
			['je.*', 'broni', '2', 'r'],
			['je.*', 'remy', '3', 'c'],
		])
		with NoPrint():
			self.client._load_responses()
		keys = list(self.client.responses.keys())
		self.assertIn(r'^!reload$', keys)
		self.assertIn(r'je.*', keys)
		self.assertEqual(len(keys), 6)

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


class TestBotCommand(unittest.IsolatedAsyncioTestCase):
	"""Test case for the BotCommand class from bot.py"""
	def setUp(self):
		self.expected = 'test callback message'
		self.callback = MagicMock(return_value = self.expected)

	async def assert_reload_command(self, content, is_admin, is_called):
		self.message = AsyncMock(content = content, author = 'moderator')
		self.message.channel.permissions_for = \
				MagicMock(return_value = MagicMock(administrator = is_admin))
		with patch.object(BotReply, 'reply_to') as bot_reply:
			command = BotCommand('^!reload$', self.callback)
			await command.reply_to(self.message)
			if is_called:
				self.callback.assert_called_with(self.message.content)
				bot_reply.assert_called_with(self.message, self.expected, True)
			else:
				self.callback.assert_not_called()
				bot_reply.assert_not_called()

	async def test_on_command_with_privilege(self):
		await self.assert_reload_command('!reload', True, True)

	async def test_on_command_with_privilege_unmatched(self):
		await self.assert_reload_command('!not-reload', True, False)

	async def test_on_command_without_privilege(self):
		await self.assert_reload_command('!reload', False, False)


class TestCsvLoader(unittest.TestCase):
	def setUp(self):
		self.loader = CsvLoader()
		self.loader.hostname = 'test_replies.csv'
		self.contents = 'honor,guides,0,me\nnot,enough,1,minerals\n'
		with open(self.loader.hostname, 'w', newline='') as csvfile:
			csvfile.write(self.contents)

	def assert_same_contents(self):
		with open(self.loader.hostname, 'r') as check:
			self.assertEqual(check.read(), self.contents)

	def test_add(self):
		entry = 'just,right,1,man'
		self.assertTrue(self.loader.add(entry))
		with open(self.loader.hostname, 'r') as check:
			self.assertEqual(check.read(), f'{self.contents}{entry}\n')

	def test_add_too_little_fields(self):
		self.assertFalse(self.loader.add('too,little'))
		self.assert_same_contents()

	def test_add_too_many_fields(self):
		self.assertFalse(self.loader.add('too,many,0,to,add'))
		self.assert_same_contents()

	def test_add_wrong_format(self):
		self.assertFalse(self.loader.add('third,field,not,digit'))
		self.assert_same_contents()

	def test_delete(self):
		self.assertTrue(self.loader.delete(1))
		with open(self.loader.hostname, 'r') as check:
			self.assertEqual(check.read(), 'honor,guides,0,me\n')

	def test_delete_not_found(self):
		self.assertFalse(self.loader.delete(2))
		self.assert_same_contents()

	def test_list(self):
		self.assertEqual(self.loader.list(False, 0),
				[['honor', 'guides', '0', 'me']])

	def test_list_all(self):
		self.assertEqual(len(self.loader.list()), 2)

	def test_list_truncate(self):
		self.assertIn('..', self.loader.list(True)[1][3])

	def test_list_invalid_index(self):
		self.assertEqual(self.loader.list(False, 2), [])

	def tearDown(self):
		try:
			os.remove('test_replies.csv')
			os.remove(self.loader.CONFIG_FILENAME)
		except FileNotFoundError:
			pass


if __name__ == '__main__':
	unittest.main(verbosity=2)
