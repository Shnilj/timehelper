import argparse
import datetime
import os
from colorama import Fore
from git_service import GitService
from devops import DevOpsService
from halo import Halo

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--date', help='The date to check in the format YYYY-MM-DD')
parser.add_argument('-t', '--tickets', help='Show the tickets that were worked on', action='store_true')
args = parser.parse_args()

def main():
    loader = Halo(text='Loading', spinner='dots')
    loader.start()

    if args.date:
        try:
            date_to_check = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format, please use YYYY-MM-DD")
            return
    else:
        date_to_check = None


    if args.tickets:
        response = DevOpsService().get_recent_activity_data()
        loader.stop()

        return response

    git_service = GitService()
    author_names = os.environ['AUTHOR_NAMES'] # replace with the name you use for git commits
    commit_dict = git_service.get_commits_for_date(date_to_check, author_names)
    for repo, commitsByHash in commit_dict.items():
        commits = commitsByHash.values()
        print(f'Repository: {repo}')
        for commit in commits:
            print(Fore.RESET + f'Branch: {commit["branch"]}, Time: {commit["time"]}')
            print(Fore.LIGHTGREEN_EX + f'Message: {commit["message"]}')
            print(('-' * 50))  # print line of dashes after each commit
            print()  # print empty line

    print(Fore.RESET)

    loader.stop()

if __name__ == '__main__':
    main()
