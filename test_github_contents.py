from betamax import Betamax
from github_contents import GithubContents


with Betamax.configure() as config:
    config.cassette_library_dir = "cassettes"


def test_read_small_file():
    github = GithubContents("simonw", "markdown-to-sqlite", "XXX")
    with Betamax(github.session) as vcr:
        vcr.use_cassette("get-file")
        content, sha = github.read("setup.cfg")
        assert b"[aliases]\ntest=pytest\n" == content
        assert "b7e478982ccf9ab1963c74e1084dfccb6e42c583" == sha
