import subprocess
from datetime import datetime, timedelta

class GitTool:
    def __init__(self, repo_path='.'):
        self.repo_path = repo_path

    def execute_git_command(self, command):
        """
        Execute a generic Git command.

        Args:
            command (list): List of command arguments.

        Returns:
            str: The output of the Git command.
        """
        result = subprocess.run(command, cwd=self.repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        return result.stdout.strip()

    def get_changes_by_author(self, author, days=7):
        """
        Get the changes made by a specific author in the last given number of days.

        Args:
            author (str): The name of the author.
            days (int): The number of days to look back from today. Default is 7.

        Returns:
            list: A list of commits by the author in the given time frame.
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        command = ['git', 'log', '--author', author, '--since', since_date, '--pretty=format:%h %s']
        return self.execute_git_command(command).split('\n')

    def get_commits_by_reference(self, ref_key):
        """
        Get all commit IDs that reference a specific key in their commit message.

        Args:
            ref_key (str): The reference key to search for (e.g., issue ID).

        Returns:
            list: A list of commits that contain the reference key.
        """
        command = ['git', 'log', '--grep', ref_key, '--pretty=format:%h %s']
        return self.execute_git_command(command).split('\n')

    def get_last_modifier(self, file_path, line_number):
        """
        Get the last modifier of a specific line in a file.

        Args:
            file_path (str): The path to the file.
            line_number (int): The line number to check.

        Returns:
            str: The name of the author who last modified the specified line.
        """
        command = ['git', 'blame', '-L', f'{line_number},{line_number}', file_path, '--porcelain']
        output = self.execute_git_command(command)
        for line in output.split('\n'):
            if line.startswith('author '):
                return line[len('author '):]

    def generate_commit_message(self, file_path):
        """
        Generate a commit message based on the changes in a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: A generated commit message describing the changes.
        """
        command = ['git', 'diff', '--name-only', 'HEAD']
        changed_files = self.execute_git_command(command).split('\n')
        
        message = f"Updated {file_path}\n\nChanges made:\n"
        for file in changed_files:
            message += f"- {file}\n"
        return message

    # Neue Funktionen

    def create_branch(self, branch_name):
        """
        Create a new branch.

        Args:
            branch_name (str): The name of the new branch.
        """
        command = ['git', 'branch', branch_name]
        self.execute_git_command(command)

    def delete_branch(self, branch_name):
        """
        Delete a branch.

        Args:
            branch_name (str): The name of the branch to delete.
        """
        command = ['git', 'branch', '-d', branch_name]
        self.execute_git_command(command)

    def list_branches(self):
        """
        List all branches.

        Returns:
            list: A list of all branches.
        """
        command = ['git', 'branch']
        return self.execute_git_command(command).split('\n')

    def switch_branch(self, branch_name):
        """
        Switch to a different branch.

        Args:
            branch_name (str): The name of the branch to switch to.
        """
        command = ['git', 'checkout', branch_name]
        self.execute_git_command(command)

    def stash_changes(self):
        """
        Stash local changes.
        """
        command = ['git', 'stash']
        self.execute_git_command(command)

    def apply_stash(self):
        """
        Apply stashed changes.
        """
        command = ['git', 'stash', 'apply']
        self.execute_git_command(command)

    # def add_remote(self, name, url):
    #     """
    #     Add a new remote repository.

    #     Args:
    #         name (str): The name of the remote.
    #         url (str): The URL of the remote.
    #     """
    #     command = ['git', 'remote', 'add', name, url]
    #     self.execute_git_command(command)

    # def remove_remote(self, name):
    #     """
    #     Remove a remote repository.

    #     Args:
    #         name (str): The name of the remote to remove.
    #     """
    #     command = ['git', 'remote', 'remove', name]
    #     self.execute_git_command(command)

    def list_remotes(self):
        """
        List all remote repositories.

        Returns:
            list: A list of all remote repositories.
        """
        command = ['git', 'remote', '-v']
        return self.execute_git_command(command).split('\n')

    def pull_changes(self, remote='origin', branch='main'):
        """
        Pull changes from a remote repository.

        Args:
            remote (str): The name of the remote. Default is 'origin'.
            branch (str): The name of the branch. Default is 'main'.
        """
        command = ['git', 'pull', remote, branch]
        self.execute_git_command(command)

    def push_changes(self, remote='origin', branch='main'):
        """
        Push changes to a remote repository.

        Args:
            remote (str): The name of the remote. Default is 'origin'.
            branch (str): The name of the branch. Default is 'main'.
        """
        command = ['git', 'push', remote, branch]
        self.execute_git_command(command)

    def get_status(self):
        """
        Get the current repository status.

        Returns:
            str: The output of the git status command.
        """
        command = ['git', 'status']
        return self.execute_git_command(command)

    def get_diff(self, file_path=None):
        """
        Get the diff of changes.

        Args:
            file_path (str): The path to a specific file to get the diff for. If None, gets the diff for all changes.

        Returns:
            str: The output of the git diff command.
        """
        command = ['git', 'diff']
        if file_path:
            command.append(file_path)
        return self.execute_git_command(command)

    def create_tag(self, tag_name, message=''):
        """
        Create a new tag.

        Args:
            tag_name (str): The name of the tag.
            message (str): A message for the tag. Default is an empty string.
        """
        command = ['git', 'tag', '-a', tag_name, '-m', message]
        self.execute_git_command(command)

    # def delete_tag(self, tag_name):
    #     """
    #     Delete a tag.

    #     Args:
    #         tag_name (str): The name of the tag to delete.
    #     """
    #     command = ['git', 'tag', '-d', tag_name]
    #     self.execute_git_command(command)

    def list_tags(self):
        """
        List all tags.

        Returns:
            list: A list of all tags.
        """
        command = ['git', 'tag']
        return self.execute_git_command(command).split('\n')

# Beispielaufruf
if __name__ == "__main__":
    git_tool = GitTool('/path/to/your/repo')

    # Änderungen des Autors 'mk' in der letzten Woche
    author_changes = git_tool.get_changes_by_author('mk')
    print("Changes by author 'mk':", author_changes)

    # Commits, die 'MEDT-1234' referenzieren
    commits = git_tool.get_commits_by_reference('MEDT-1234')
    print("Commits referencing 'MEDT-1234':", commits)

    # Letzter Modifier der Zeile 144 in der Datei XYZ
    modifier = git_tool.get_last_modifier('path/to/file/XYZ', 144)
    print("Last modifier of line 144 in XYZ:", modifier)

    # Generierte Commit-Nachricht
    commit_message = git_tool.generate_commit_message('path/to/file/XYZ')
    print("Generated commit message:", commit_message)

    # Weitere Funktionen
    git_tool.create_branch('new-feature')
    git_tool.switch_branch('new-feature')
    branches = git_tool.list_branches()
    print("Branches:", branches)

    git_tool.stash_changes()
    git_tool.apply_st
