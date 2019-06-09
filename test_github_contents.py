from betamax import Betamax
from github_contents import GithubContents
import pathlib
import os
import json


TOKEN = os.environ.get("TEST_GITHUB_TOKEN") or "XXX"

with Betamax.configure() as config:
    config.cassette_library_dir = "cassettes"


def test_read_small_file():
    github = GithubContents("simonw", "github-contents-demo", TOKEN)
    with Betamax(github.session) as vcr:
        vcr.use_cassette("get-file")
        content, sha = github.read("hello.txt")
    assert b"hello world again" == content
    assert "ef38e9e4a6464f8fc7d0d7ff80aa998953291393" == sha


def test_write_small_file():
    github = GithubContents("simonw", "github-contents-demo", TOKEN)
    with Betamax(github.session) as vcr:
        vcr.use_cassette("write-file")
        assert (
            "3c840b722385abe67a2cfadac6a8eaab8429a45c",
            "31d05dc55bac68b73cb9584611dd4c41b9ca6600",
        ) == github.write(
            "hello.txt",
            b"hello world 3",
            commit_message="updated by test",
            committer={"name": "Test", "email": "test"},
        )


def test_no_accidental_oauth_token_in_cassettes():
    # Need to make sure I never accidentally check my OAuth token into GitHub
    for filepath in pathlib.Path("cassettes").glob("*.json"):
        data = json.loads(filepath.read_text())
        for interaction in data["http_interactions"]:
            for header in interaction["request"]["headers"].get("Authorization") or []:
                assert "token XXX" == header
