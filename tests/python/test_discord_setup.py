"""Offline tests for the embeds posted by scripts/discord_setup.py."""

import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "discord_setup.py"
SPEC = importlib.util.spec_from_file_location("discord_setup", SCRIPT)
assert SPEC and SPEC.loader
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class TestEmbeds(unittest.TestCase):
    def test_offline_previews_every_outgoing_message(self):
        # Exercise both a continuation and a channel omitted by the old preview.
        long_rule = "x" * (setup.EMBED_LIMIT + 1)
        sections = {"welcome": "Welcome!", "rules": long_rule, "faq": "End of the FAQ. 🎵"}
        markdown = "\n\n".join(f"## {heading}\n\n> {sections[channel]}"
                               for channel, heading in setup.MESSAGES.items())
        output = io.TextIOWrapper(io.BytesIO(), encoding="ascii", write_through=True)
        with mock.patch.object(setup, "DOC") as doc, mock.patch.object(setup, "Discord") as api, \
                mock.patch.object(sys, "argv", ["discord_setup.py", "--offline"]), redirect_stdout(output):
            doc.read_text.return_value = markdown
            self.assertEqual(setup.main(), 0)
        api.assert_not_called()
        summary, separator, data = output.buffer.getvalue().decode("ascii").partition("\n{")
        self.assertIn("#rules: 2 embed(s)", summary)
        self.assertTrue(separator, "Expected the full preview keyed by channel")
        preview = json.loads("{" + data)
        self.assertEqual(set(preview), set(sections))
        for channel, expected in sections.items():
            messages = preview[channel]
            self.assertEqual("".join(post["embeds"][0]["description"] for post in messages), expected)
            self.assertEqual(messages[0]["embeds"][0]["title"], setup.MESSAGES[channel])
            self.assertTrue(all(post["allowed_mentions"] == {"parse": []} for post in messages))
        self.assertNotIn("title", preview["rules"][1]["embeds"][0])

    def test_exact_limit_and_paragraph_breaks(self):
        limit = setup.EMBED_LIMIT
        first = "a" * (limit - 3) + "\n\nb"
        embeds = setup.embeds_for(first + "\n\nend", "FAQ")
        self.assertEqual([e["description"] for e in embeds], [first, "end"])
        self.assertEqual([e["title"] for e in embeds], ["FAQ", None])

    def test_long_unbroken_paragraph_between_short_ones(self):
        limit = setup.EMBED_LIMIT
        paragraph = "x" * (2 * limit + 1)
        embeds = setup.embeds_for("intro\n\n" + paragraph + "\n\nend", "Rules")
        self.assertEqual([e["description"] for e in embeds],
                         ["intro", "x" * limit, "x" * limit, "x\n\nend"])

    def test_long_paragraph_preserves_words_and_line_breaks(self):
        paragraph = "one two\tthree\nfour " * 300
        embeds = setup.embeds_for(paragraph, "Welcome")
        parts = [e["description"] for e in embeds]
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(0 < len(p) <= setup.EMBED_LIMIT for p in parts))
        self.assertEqual("".join(parts), paragraph)
        for left, right in zip(parts, parts[1:]):
            self.assertTrue(left[-1].isspace() or right[0].isspace())


if __name__ == "__main__":
    unittest.main()
