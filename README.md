# github-contents

[![PyPI](https://img.shields.io/pypi/v/github-contents.svg)](https://pypi.org/project/github-contents/)
[![CircleCI](https://circleci.com/gh/simonw/github-contents.svg?style=svg)](https://circleci.com/gh/simonw/github-contents)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-json-html/blob/master/LICENSE)

Read and write both small and large files to Github.

The regular [GitHub Contents API](https://developer.github.com/v3/repos/contents/) can't handle files larger than 1MB - this class knows how to spot that problem and switch to the large-file-supporting low level [Git Data API](https://developer.github.com/v3/git/) instead.

Note that file contents is passed and returned as bytestrings, not regular strings.

## Installation

    pip install github-contents

## Usage

You will need a GitHub OAuth token with full repository access.

The easiest way to create one of these is using [https://github.com/settings/tokens](https://github.com/settings/tokens)

```python
from github_contents import GitubContents

# For repo simonw/disaster-data:
github = GithubContents(
    "simonw",
    "disaster-data",
    GITHUB_OAUTH_TOKEN
)
```
To read a file:
```python
content_in_bytes, sha = github.read(path_within_repo)
```
To write a file:
```python
content_sha, commit_sha = github.write(
    filepath=path_within_repo,
    content_bytes=contents_in_bytes,
    sha=previous_sha, # Optional
    commit_message=commit_message,
    committer={
        "name": COMMITTER_NAME,
        "email": COMMITTER_EMAIL,
    },
)
```
