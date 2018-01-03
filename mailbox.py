from zeromail import ZeroMail
from message import Message
from config import zeronet_directory
import zeronet
from pop3.util import CommandError

class Mailbox(object):
	def __init__(self, user, password):
		self.user = user
		self.password = password

		if user == "local" and password == "local":
			self.user, self.password = zeronet.guess_private_key(zeronet_directory)
			if self.user is None:
				raise CommandError("Failed to access users.json")
			elif self.password is None:
				raise CommandError("Could not find user passwords")
		elif user == "local":
			self.user, _ = zeronet.guess_private_key(zeronet_directory)
			if self.user is None:
				raise CommandError("Failed to access users.json")
		elif password == "local":
			zeroid, self.password = zeronet.guess_private_key(zeronet_directory)
			if zeroid is None:
				raise CommandError("Failed to access users.json")
			elif self.password is None:
				raise CommandError("Could not find user passwords")

		self.zeromail = ZeroMail(zeronet_directory, zeroid=self.user, priv=self.password)
		self.message_ids = dict()

	def load_messages(self):
		secrets = self.zeromail.update_secrets()
		messages = self.zeromail.update_messages(secrets)
		messages = {date: Message(int(date), data) for date, data in messages.iteritems()}
		return messages

	def messageCount(self):
		return len(self.load_messages())
	def __len__(self):
		return sum([len(message) for message in self.load_messages()])

	def getMessageIds(self):
		self.message_ids = dict(enumerate(self.load_messages().keys()))
		return self.message_ids.keys()
	def expandMessageId(self, message):
		self.load_messages()
		try:
			return self.message_ids[int(message)]
		except KeyError:
			return None

	def __contains__(self, message):
		messages = self.load_messages()
		message_id = self.expandMessageId(message)
		return message_id is not None and message_id in messages
	def __getitem__(self, message):
		messages = self.load_messages()
		return messages[self.expandMessageId(message)]

	def pop(self, message):
		secrets = self.zeromail.update_secrets()
		self.zeromail.remove_message(secrets, self.expandMessageId(message))