# github-contents

[![PyPI](https://img.shields.io/pypi/v/github-contents.svg)](https://pypi.org/project/github-contents/)
[![Travis CI](https://travis-ci.com/simonw/github-contents.svg?branch=master)](https://travis-ci.com/simonw/github-contents)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-json-html/blob/master/LICENSE)

Read and write both small and large files to Github.

The regular [GitHub Contents API](https://developer.github.com/v3/repos/contents/) can't handle files larger than 1MB - this class knows how to spot that proble and switch to the large-file-supporting low level [Git Data API](https://developer.github.com/v3/git/) instead.

## Usage

```python
# For repo simonw/disaster-data:
github = GithubContents(
    "simonw",
    "disaster-data",
    GITHUB_OAUTH_TOKEN
)
```
To read a file:
```python
content, sha = github.read(path_within_repo)
```
To write a file:
```python
content_sha, commit_sha = github.write(
    filepath=path_within_repo,
    content=contents,
    sha=previous_sha, # Optional
    commit_message=commit_message,
    committer={
        "name": COMMITTER_NAME,
        "email": COMMITTER_EMAIL,
    },
)
```
