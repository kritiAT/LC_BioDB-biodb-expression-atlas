#!/usr/bin/env python

"""Tests for `biodb_expression_atlas` package."""


import unittest
from click.testing import CliRunner

from biodb_expression_atlas import biodb_expression_atlas
from biodb_expression_atlas import cli


class TestBiodb_expression_atlas(unittest.TestCase):
    """Tests for `biodb_expression_atlas` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'biodb_expression_atlas.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
