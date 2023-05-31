
import base64
import io
import yaml

from github import Github, GithubIntegration

if __name__ == '__main__':

    with open("rafael-sync-back.2023-05-30.private-key.pem", "r") as secret:
        private_key = secret.read()

    GITHUB_APP_ID = "340716"
    integration = GithubIntegration(GITHUB_APP_ID, private_key)

    owner_name = "rafpires-corp"   # the org on my personal account
    repo_name = "my_dbt_demo"

    git_connection = Github(
        login_or_token=integration.get_access_token(
            integration.get_repo_installation(owner_name, repo_name).id
        ).token
    )

    repo = git_connection.get_repo(f"{owner_name}/{repo_name}")

    # get the name of the default branch: "master", "main", "whatever"
    default_branch_name = repo.default_branch

    # the new branch to be used
    new_branch_name = "raf2"

    # full name of the new branch
    new_branch_ref = f'refs/heads/{new_branch_name}'

    # create the new branch from the default_branch, if needed
    # repo.create_git_ref(ref=new_branch_ref, sha=default_branch.commit.sha)

    # get the file that I want to change, from the new branch
    f_content = repo.get_contents("models/test_source/test.yml", ref=new_branch_ref)

    # have to convert the content out of b64
    base64_bytes = f_content.content.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')

    # write the file locally, can be skipped
    with open(file="original.yml", mode="w") as f:
        f.write(message)

    # load the yaml file
    x = yaml.load(message, yaml.FullLoader)

    # write the yaml file locally, can be skipped
    with open('modified.yml', mode='w', encoding="utf-8") as f:
        yaml.dump(x, f, encoding="utf-8", sort_keys=False, indent=2)

    # write the yaml file to a str
    content_back = io.StringIO()
    yaml.dump(x, content_back, encoding="utf-8", sort_keys=False, indent=2)

    # update the yaml file in the new branch
    repo.update_file(path="models/test_source/test.yml", message="new desc", content=content_back.getvalue(),
                     branch=new_branch_name, sha=f_content.sha)

    # open a pull request new branch -> default branch
    repo.create_pull(title="My 1st pull", body="This is the body of the pull!!", head=new_branch_name,
                     base=default_branch_name, draft=False)
