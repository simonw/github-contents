from betamax import Betamax
from github_contents import GithubContents
import pathlib
import os
import json


TOKEN = os.environ.get("TEST_GITHUB_TOKEN") or "XXX"

# When recording new tests, run the test suite with
# VCR_RECORD=new_episodes TEST_GITHUB_TOKEN=... pytest -k name_of_test
# https://betamax.readthedocs.io/en/latest/record_modes.html
VCR_RECORD = os.environ.get("VCR_RECORD") or "none"

with Betamax.configure() as config:
    config.cassette_library_dir = "cassettes"


def test_read_small_file():
    github = GithubContents("simonw", "github-contents-demo", TOKEN)
    with Betamax(github.session) as vcr:
        vcr.use_cassette("get-file")
        content, sha = github.read("hello.txt")
    assert b"hello world 3" == content
    assert "3c840b722385abe67a2cfadac6a8eaab8429a45c" == sha


def test_write_small_file():
    github = GithubContents("simonw", "github-contents-demo", TOKEN)
    with Betamax(github.session) as vcr:
        vcr.use_cassette("write-file")
        assert (
            "3c840b722385abe67a2cfadac6a8eaab8429a45c",
            "ba288b9c0a35409bf655bc85b5b6b04db7bb7742",
        ) == github.write(
            "hello.txt",
            b"hello world 3",
            commit_message="updated by test",
            committer={"name": "Test", "email": "test"},
        )


def test_write_large():
    github = GithubContents("simonw", "github-contents-demo", TOKEN)
    with Betamax(github.session) as vcr:
        vcr.use_cassette("write-file-large")
        assert (
            "659974e29c1fd07322c9adf7de6636c6c0c8f9d8",
            "16b273de7090b618be4924e05b5763a9f4c4c69b",
        ) == github.write_large(
            "write_large.txt",
            b"not actually large but I did use the .write_large() method",
            commit_message="written by test",
            committer={"name": "Test", "email": "test"},
        )


def test_branch_exists_returns_false_for_nonexistant_branch():
    github = GithubContents(
        "simonw", "github-contents-demo", TOKEN, branch="not-a-branch"
    )
    with Betamax(github.session) as vcr:
        vcr.use_cassette("branch-exists-false.json", record=VCR_RECORD)
        assert not github.branch_exists()


def test_branch_exists_returns_true_for_existing_branch():
    github = GithubContents(
        "simonw", "github-contents-demo", TOKEN, branch="demo-branch"
    )
    with Betamax(github.session) as vcr:
        vcr.use_cassette("branch-exists-true.json", record=VCR_RECORD)
        assert github.branch_exists()


def test_no_accidental_oauth_token_in_cassettes():
    # Need to make sure I never accidentally check my OAuth token into GitHub
    for filepath in pathlib.Path("cassettes").glob("*.json"):
        data = json.loads(filepath.read_text())
        for interaction in data["http_interactions"]:
            for header in interaction["request"]["headers"].get("Authorization") or []:
                assert "token XXX" == header
