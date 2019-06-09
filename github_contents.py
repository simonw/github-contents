import base64
from requests import Session


class GithubContents:
    class NotFound(Exception):
        pass

    class UnknownError(Exception):
        pass

    def __init__(self, owner, repo, token):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.session = Session()

    def base_url(self):
        return "https://api.github.com/repos/{}/{}".format(self.owner, self.repo)

    def headers(self):
        return {"Authorization": "token {}".format(self.token)}

    def read(self, filepath):
        "Returns (file_contents_in_bytes, sha1)"
        # Try reading using content API
        content_url = "{}/contents/{}".format(self.base_url(), filepath)
        response = self.session.get(content_url, headers=self.headers())
        if response.status_code == 200:
            data = response.json()
            return base64.b64decode(data["content"]), data["sha"]
        elif response.status_code == 404:
            raise self.NotFound(filepath)
        elif response.status_code == 403:
            # It's probably too large
            if response.json()["errors"][0]["code"] != "too_large":
                raise self.UnknownError(response.content)
            else:
                return self.read_large(filepath)
        else:
            raise self.UnknownError(response.content)

    def read_large(self, filepath):
        master = self.session.get(
            self.base_url() + "/git/trees/master?recursive=1", headers=self.headers()
        ).json()
        try:
            tree_entry = [t for t in master["tree"] if t["path"] == filepath][0]
        except IndexError:
            raise self.NotFound(filepath)
        data = self.session.get(tree_entry["url"], headers=self.headers()).json()
        return base64.b64decode(data["content"]), data["sha"]

    def write(
        self, filepath, content_bytes, sha=None, commit_message="", committer=None
    ):
        if not isinstance(content_bytes, bytes):
            raise TypeError("content_bytes must be a bytestring")
        github_url = "{}/contents/{}".format(self.base_url(), filepath)
        payload = {
            "path": filepath,
            "content": base64.b64encode(content_bytes).decode("latin1"),
            "message": commit_message,
        }
        if sha:
            payload["sha"] = sha
        if committer:
            payload["committer"] = committer

        response = self.session.put(github_url, json=payload, headers=self.headers())
        if (
            response.status_code == 403
            and response.json()["errors"][0]["code"] == "too_large"
        ):
            return self.write_large(filepath, content_bytes, commit_message, committer)
        elif (
            sha is None
            and response.status_code == 422
            and "sha" in response.json().get("message", "")
        ):
            # Missing sha - we need to figure out the sha and try again
            _, old_sha = self.read(filepath)
            return self.write(
                filepath,
                content_bytes,
                sha=old_sha,
                commit_message=commit_message,
                committer=committer,
            )
        elif response.status_code in (201, 200):
            updated = response.json()
            return updated["content"]["sha"], updated["commit"]["sha"]
        else:
            raise self.UnknownError(
                str(response.status_code) + ":" + repr(response.content)
            )

    def write_large(self, filepath, content_bytes, commit_message="", committer=None):
        if not isinstance(content_bytes, bytes):
            raise TypeError("content_bytes must be a bytestring")
        # Create a new blob with the file contents
        created_blob = self.session.post(
            self.base_url() + "/git/blobs",
            json={
                "encoding": "base64",
                "content": base64.b64encode(content_bytes).decode("latin1"),
            },
            headers=self.headers(),
        ).json()
        # Retrieve master tree sha
        master_sha = self.session.get(
            self.base_url() + "/git/trees/master?recursive=1", headers=self.headers()
        ).json()["sha"]
        # Construct a new tree
        created_tree = self.session.post(
            self.base_url() + "/git/trees",
            json={
                "base_tree": master_sha,
                "tree": [
                    {
                        "mode": "100644",  # file (blob),
                        "path": filepath,
                        "type": "blob",
                        "sha": created_blob["sha"],
                    }
                ],
            },
            headers=self.headers(),
        ).json()
        # Create a commit which references the new tree
        payload = {
            "message": commit_message,
            "parents": [master_sha],
            "tree": created_tree["sha"],
        }
        if committer:
            payload["committer"] = committer
        created_commit = self.session.post(
            self.base_url() + "/git/commits", json=payload, headers=self.headers()
        ).json()
        # Move HEAD reference on master to the new commit
        self.session.patch(
            self.base_url() + "/git/refs/heads/master",
            json={"sha": created_commit["sha"]},
            headers=self.headers(),
        ).json()
        return created_blob["sha"], created_commit["sha"]
