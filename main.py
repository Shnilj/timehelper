import argparse
import datetime
from colorama import Fore
from git_service import GitService
from devops import DevOpsService

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--date', help='The date to check in the format YYYY-MM-DD')
parser.add_argument('-t', '--tickets', help='Show the tickets that were worked on', action='store_true')
args = parser.parse_args()

def main():
    if args.date:
        try:
            date_to_check = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format, please use YYYY-MM-DD")
            return
    else:
        date_to_check = None

    if args.tickets:
        return DevOpsService().get_recent_activity_data()

    git_service = GitService()
    author_name = "Jens Descamps"  # replace with the name you use for git commits
    commit_dict = git_service.get_commits_for_date(date_to_check, author_name)
    for repo, commits in commit_dict.items():
        print(f'Repository: {repo}')
        for commit in commits:
            print(Fore.RESET + f'Branch: {commit["branch"]}, Time: {commit["time"]}')
            print(Fore.LIGHTGREEN_EX + f'Message: {commit["message"]}')
            print(('-' * 50))  # print line of dashes after each commit
            print()  # print empty line

if __name__ == '__main__':
    main()
