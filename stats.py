import getpass
from pathlib import Path
from pprint import pprint

from dateutil.parser import parse as dtparse
import github3

token_path = Path('/tmp/ghstats.token')

target_repos = [
    ('lablup', 'backend.ai'),
    ('lablup', 'backend.ai-manager'),
    ('lablup', 'backend.ai-agent'),
    ('lablup', 'backend.ai-common'),
    ('lablup', 'backend.ai-kernels'),
    ('lablup', 'backend.ai-console'),
    ('lablup', 'backend.ai-console-server'),
    ('lablup', 'backend.ai-accelerator-cuda'),
]
filter_user = 'achimnol'
raw_start_date = '2019-05-16T00:00:00+09:00'
raw_end_date = '2019-12-06T23:59:59+09:00'


def my_two_factor_function():
    code = ''
    while not code:
        code = input('Enter 2FA code: ')
    return code


issue_open_count = 0
commit_count = 0
pr_count = 0
merge_count = 0
review_count = 0


def stat_repo(user_or_org, repo_name):
    global issue_open_count, commit_count, pr_count, merge_count, review_count
    repo_issue_open_count = 0
    repo_commit_count = 0
    repo_pr_count = 0
    repo_merge_count = 0
    repo_review_count = 0

    start_date = dtparse(raw_start_date)
    end_date = dtparse(raw_end_date)

    print()
    print(f'Fetching data from {user_or_org}/{repo_name}...')
    repo = gh.repository(user_or_org, repo_name)
    for issue in repo.issues(since=raw_start_date):
        if issue.user.login == filter_user and (issue.created_at <= end_date):
            repo_issue_open_count += 1
    for commit in repo.commits(since=raw_start_date):
        if commit.author is not None and commit.author.login == filter_user and (dtparse(commit.commit.author['date']) <= end_date):
            repo_commit_count += 1
    for pr in repo.pull_requests(state='all'):
        if pr.user.login == filter_user:
            if (start_date <= pr.created_at <= end_date):
                repo_pr_count += 1
            if pr.merged_at is not None and (start_date <= pr.merged_at <= end_date):
                repo_merge_count += 1
        for review in pr.reviews():
            if review.user.login == filter_user and (start_date <= review.submitted_at <= end_date):
                repo_review_count += 1

    print(f' => Per-repo user statistics for {filter_user}')
    print(f'     - Opened issues: {repo_issue_open_count}')
    print(f'     - Commits: {repo_commit_count}')
    print(f'     - Opened PRs: {repo_pr_count}')
    print(f'     - Merged PRs: {repo_merge_count}')
    print(f'     - Submitted reviews: {repo_review_count}')
    issue_open_count += repo_issue_open_count
    commit_count += repo_commit_count
    pr_count += repo_pr_count
    merge_count += repo_merge_count
    review_count += repo_review_count


if __name__ == '__main__':
    scopes = ['repo']
    token = None
    try:
        token = token_path.read_text()
    except IOError:
        pass

    if token is None:
        username = input('Username: ')
        password = getpass.getpass()
        gh = github3.login(
            username,
            password,
            two_factor_callback=my_two_factor_function)
        auth = gh.authorize(username, password, scopes, 'ghstats', 'https://github.com/achimnol/ghstats')
        token_path.write_text(auth.token)
        token = auth.token

    gh = github3.login(token=token)

    print(f'Configured date range: {raw_start_date} to {raw_end_date}')

    for repo in target_repos:
        stat_repo(*repo)

    print()
    print(f'Total user statistics for {filter_user}')
    print(f' - Total opened issues: {issue_open_count}')
    print(f' - Total commits: {commit_count}')
    print(f' - Opened PRs: {pr_count}')
    print(f' - Merged PRs: {merge_count}')
    print(f' - Submitted reviews: {review_count}')
