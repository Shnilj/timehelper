import datetime
from git import Repo
import json

class GitService:

    with open('git_config.json') as f:
        config = json.load(f)

    branch = config['branch']
    repositories = config['repositories']

    def init(self):
        print("GitService init")

    def set_branch(self, branch):
        self.branch = branch

        return self
    
    def set_repositories(self, repositories):
        self.repositories = repositories

        return self

    def get_commits_for_date(self, date, author):
        today = datetime.date.today()
        if date is None:
            date = today - datetime.timedelta(days=7)

        commit_dict = {}

        for repository in self.repositories:
            repo = Repo(repository)

            for commit in repo.iter_commits():
                if commit.author.name == author:
                    commit_datetime = datetime.datetime.fromtimestamp(commit.authored_date)
                    if date <= commit_datetime.date() <= today:
                        if repository not in commit_dict:
                            commit_dict[repository] = []
                        commit_dict[repository].append({
                            'hash': commit.hexsha,
                            'message': commit.message,
                            'time': commit_datetime.strftime('%d/%m/%Y %H:%M:%S'),
                            'branch': commit.repo.active_branch.name
                        })

        for repository in commit_dict:
            commit_dict[repository] = sorted(commit_dict[repository], key=lambda k: k['time'])

        return commit_dict
