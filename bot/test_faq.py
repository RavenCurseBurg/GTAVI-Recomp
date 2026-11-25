import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch

import discord

import cal_hampton as cal


class FAQTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = cal.CalHampton(123)
        self.command = self.bot.tree.get_command("faq")
        self.interaction = MagicMock(spec=discord.Interaction)
        self.interaction.response = MagicMock(spec=discord.InteractionResponse)
        self.interaction.followup = MagicMock(spec=discord.Webhook)
        self.pairs = [("Which platforms?", "Windows and Linux.")]

    async def asyncTearDown(self):
        await self.bot.close()

    async def test_cold_answer_acknowledges_before_fetch_and_posts_publicly(self):
        async def fetch(session):
            self.interaction.response.send_message.assert_awaited_once()
            self.assertTrue(self.interaction.response.send_message.await_args.kwargs["ephemeral"])
            self.interaction.followup.send.assert_not_awaited()
            return self.pairs

        with patch.object(self.bot.faq, "get", side_effect=fetch):
            await self.command.callback(self.interaction, "platforms")
        self.interaction.followup.send.assert_awaited_once()
        message = self.interaction.followup.send.await_args.kwargs
        self.assertFalse(message.get("ephemeral", False))
        self.assertEqual(message["embed"].description, self.pairs[0][1])
        self.assertEqual(message["allowed_mentions"].to_dict(), discord.AllowedMentions.none().to_dict())
        self.interaction.delete_original_response.assert_awaited_once()

    async def test_cold_list_and_errors_only_edit_the_private_reply(self):
        for topic, failure in [(None, None), ("unmatched", None), ("platforms", OSError())]:
            with self.subTest(topic=topic, failure=failure):
                self.interaction.reset_mock()
                with patch.object(self.bot.faq, "get", return_value=self.pairs, side_effect=failure):
                    await self.command.callback(self.interaction, topic)
                self.interaction.response.send_message.assert_awaited_once()
                self.assertTrue(self.interaction.response.send_message.await_args.kwargs["ephemeral"])
                self.interaction.edit_original_response.assert_awaited_once()
                message = self.interaction.edit_original_response.await_args.kwargs
                if topic is None:
                    self.assertIsNone(message["content"])
                    self.assertIn(self.pairs[0][0], message["embed"].description)
                else:
                    self.assertIn("couldn't load" if failure else "don't have an answer", message["content"])
                self.interaction.followup.send.assert_not_awaited()

    async def test_fresh_cache_answers_in_one_response(self):
        self.bot.faq.value = self.pairs
        self.bot.faq.fetched = time.monotonic()
        for topic, private in [(None, True), ("platforms", False), ("unmatched", True)]:
            with self.subTest(topic=topic):
                self.interaction.reset_mock()
                await self.command.callback(self.interaction, topic)
                self.interaction.response.send_message.assert_awaited_once()
                self.assertEqual(self.interaction.response.send_message.await_args.kwargs.get("ephemeral", False),
                                 private)
                self.interaction.followup.send.assert_not_awaited()

    async def test_slow_autocomplete_can_use_the_previous_choices(self):
        for previous in [None, self.pairs]:
            with self.subTest(previous=previous):
                self.bot.faq.value = previous
                blocked = asyncio.Event()

                async def fetch(session):
                    await blocked.wait()

                with patch.object(self.bot.faq, "get", new=fetch), patch.object(cal, "FAQ_AUTOCOMPLETE_TIMEOUT", 0.01):
                    callback = self.command._params["topic"].autocomplete
                    choices = await asyncio.wait_for(callback(self.interaction, "platform"), 1)
                self.assertEqual([choice.value for choice in choices], [self.pairs[0][0]] if previous else [])
