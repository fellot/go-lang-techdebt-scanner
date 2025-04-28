"""
Git Analyzer

Analyzes Git history to determine code churn and stability metrics.
"""

import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict

class GitAnalyzer:
    """Analyzer for Git repositories."""
    
    def __init__(self, repo_path):
        """Initialize the Git analyzer.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = repo_path
    
    def _run_git_command(self, cmd):
        """Run a git command and return its output."""
        full_cmd = ['git'] + cmd
        try:
            result = subprocess.run(
                full_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def get_file_churn(self, file_path, days=90):
        """Get churn metrics for a specific file.
        
        Args:
            file_path: Path to the file
            days: Number of days to analyze
            
        Returns:
            Dictionary with churn metrics
        """
        # Get the date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get commit history for the file
        cmd = [
            'log', 
            f'--since={since_date}', 
            '--format=%H|%an|%ad|%s', 
            '--date=short', 
            '--', 
            file_path
        ]
        output = self._run_git_command(cmd)
        
        commits = []
        for line in output.splitlines():
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3]
                    })
        
        # Get line changes
        total_additions = 0
        total_deletions = 0
        
        for commit in commits:
            cmd = ['show', '--numstat', '--format=', commit['hash'], '--', file_path]
            output = self._run_git_command(cmd)
            
            for line in output.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            additions = int(parts[0]) if parts[0] != '-' else 0
                            deletions = int(parts[1]) if parts[1] != '-' else 0
                            total_additions += additions
                            total_deletions += deletions
                        except ValueError:
                            pass
        
        # Calculate churn rate
        churn_rate = (total_additions + total_deletions) / max(1, len(commits))
        
        return {
            'commits': len(commits),
            'additions': total_additions,
            'deletions': total_deletions,
            'churn_rate': churn_rate
        }
    
    def get_repo_churn(self, days=90, file_extension='.go'):
        """Get churn metrics for the entire repository.
        
        Args:
            days: Number of days to analyze
            file_extension: Filter by file extension
            
        Returns:
            Dictionary with churn metrics
        """
        # Get the date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get commit count
        cmd = ['rev-list', '--count', f'--since={since_date}', 'HEAD']
        output = self._run_git_command(cmd)
        commit_count = int(output.strip()) if output.strip().isdigit() else 0
        
        # Get author count
        cmd = [
            'shortlog', 
            '-sn', 
            f'--since={since_date}', 
            'HEAD'
        ]
        output = self._run_git_command(cmd)
        author_count = len(output.splitlines())
        
        # Get file changes
        cmd = [
            'log', 
            f'--since={since_date}', 
            '--numstat', 
            '--format=%H'
        ]
        output = self._run_git_command(cmd)
        
        total_additions = 0
        total_deletions = 0
        file_changes = defaultdict(lambda: {'additions': 0, 'deletions': 0, 'commits': 0})
        current_commit = None
        
        for line in output.splitlines():
            if re.match(r'^[0-9a-f]{40}$', line):
                current_commit = line
            elif line.strip() and current_commit:
                parts = line.split()
                if len(parts) >= 3:
                    file_path = parts[2]
                    if file_path.endswith(file_extension):
                        try:
                            additions = int(parts[0]) if parts[0] != '-' else 0
                            deletions = int(parts[1]) if parts[1] != '-' else 0
                            
                            total_additions += additions
                            total_deletions += deletions
                            
                            file_changes[file_path]['additions'] += additions
                            file_changes[file_path]['deletions'] += deletions
                            file_changes[file_path]['commits'] += 1
                        except ValueError:
                            pass
        
        # Calculate hotspots (files with high churn)
        hotspots = []
        for file_path, changes in file_changes.items():
            churn = changes['additions'] + changes['deletions']
            if churn > 0:
                hotspots.append({
                    'file': file_path,
                    'churn': churn,
                    'commits': changes['commits']
                })
        
        # Sort hotspots by churn
        hotspots.sort(key=lambda x: x['churn'], reverse=True)
        
        # Calculate churn rate
        churn_rate = (total_additions + total_deletions) / max(1, commit_count)
        
        return {
            'commit_count': commit_count,
            'author_count': author_count,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'churn_rate': churn_rate,
            'hotspots': hotspots[:10]  # Top 10 hotspots
        }
    
    def get_file_age(self, file_path):
        """Get the age of a file in days."""
        cmd = ['log', '--follow', '--format=%ad', '--date=short', '--reverse', '--', file_path]
        output = self._run_git_command(cmd)
        
        if not output:
            return 0
        
        first_commit_date = output.splitlines()[0]
        try:
            first_date = datetime.strptime(first_commit_date, '%Y-%m-%d')
            age_days = (datetime.now() - first_date).days
            return age_days
        except ValueError:
            return 0
    
    def get_file_contributors(self, file_path):
        """Get the number of contributors to a file."""
        cmd = ['shortlog', '-sn', '--', file_path]
        output = self._run_git_command(cmd)
        
        return len(output.splitlines())