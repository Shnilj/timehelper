import datetime
from git import Repo
import json

class GitService:

    with open('git_config.json') as f:
        config = json.load(f)

    repositories = config['repositories']
    dateRange = False

    def init(self):
        print("GitService init")

    def set_repositories(self, repositories):
        self.repositories = repositories

        return self

    def get_commits_for_date(self, date, authors):
        today = datetime.date.today()
        if date is None:
            date = today - datetime.timedelta(days=7)
            self.dateRange = True

        commit_dict = {}

        for repository in self.repositories:
            repo = Repo(repository)
            unmerged = repo.git.branch('--no-merged');
            unmerged = ['develop'] + unmerged.split('\n')

            for branch in unmerged:
                for commit in repo.iter_commits(branch.strip()):
                    commit_datetime = datetime.datetime.fromtimestamp(commit.authored_date)
                    if (self.dateRange == True and date <= commit_datetime.date() <= today) or (self.dateRange == False and date == commit_datetime.date()):
                        if commit.author.name in authors:
                            if repository not in commit_dict:
                                commit_dict[repository] = {}
                            if(commit.hexsha not in commit_dict[repository]):
                                commit_dict[repository][commit.hexsha] = {
                                    'hash': commit.hexsha,
                                    'message': commit.message,
                                    'time': commit_datetime.strftime('%d/%m/%Y %H:%M:%S'),
                                    'branch': commit.repo.active_branch.name
                                }

        # for repository in commit_dict:
        #     commit_dict[repository] = sorted(commit_dict[repository], key=lambda k: k['time'])

        return commit_dict
