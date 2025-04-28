"""
Go Tools Integration

Provides interfaces to various Go analysis tools.
"""

import subprocess
import json
import os
import re
from pathlib import Path

class GoToolRunner:
    """Runner for Go analysis tools."""
    
    @staticmethod
    def run_command(cmd, cwd=None, capture_output=True):
        """Run a shell command and return its output."""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Some tools return non-zero exit codes when they find issues
            # which is actually what we want
            return e.stdout
    
    @staticmethod
    def run_gocyclo(repo_path, threshold=15):
        """Run gocyclo to measure cyclomatic complexity."""
        cmd = ['gocyclo', '-over', str(threshold), '-avg', repo_path]
        output = GoToolRunner.run_command(cmd)
        
        # Parse the output
        results = []
        avg_complexity = 0
        
        for line in output.splitlines():
            if line.startswith('Average'):
                avg_match = re.search(r'Average: (\d+\.\d+)', line)
                if avg_match:
                    avg_complexity = float(avg_match.group(1))
            else:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        complexity = int(parts[0])
                        file_info = ' '.join(parts[1:])
                        results.append({
                            'complexity': complexity,
                            'file_info': file_info
                        })
                    except (ValueError, IndexError):
                        pass
        
        return {
            'average_complexity': avg_complexity,
            'functions': results
        }
    
    @staticmethod
    def run_gocognit(repo_path, threshold=15):
        """Run gocognit to measure cognitive complexity."""
        cmd = ['gocognit', '-over', str(threshold), '-avg', repo_path]
        output = GoToolRunner.run_command(cmd)
        
        # Parse the output
        results = []
        avg_complexity = 0
        
        for line in output.splitlines():
            if line.startswith('Average'):
                avg_match = re.search(r'Average: (\d+\.\d+)', line)
                if avg_match:
                    avg_complexity = float(avg_match.group(1))
            else:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        complexity = int(parts[0])
                        file_info = ' '.join(parts[1:])
                        results.append({
                            'complexity': complexity,
                            'file_info': file_info
                        })
                    except (ValueError, IndexError):
                        pass
        
        return {
            'average_complexity': avg_complexity,
            'functions': results
        }
    
    @staticmethod
    def run_scc(repo_path):
        """Run scc (Sloc, Cloc and Code) for various metrics."""
        cmd = ['scc', '--format', 'json', repo_path]
        output = GoToolRunner.run_command(cmd)
        
        try:
            results = json.loads(output)
            # Filter for Go files only
            go_results = [r for r in results if r.get('Language') == 'Go']
            return go_results
        except json.JSONDecodeError:
            return []
    
    @staticmethod
    def run_golangci_lint(repo_path):
        """Run golangci-lint for comprehensive linting."""
        cmd = ['golangci-lint', 'run', '--out-format', 'json', repo_path]
        output = GoToolRunner.run_command(cmd, cwd=repo_path)
        
        try:
            results = json.loads(output)
            return results
        except json.JSONDecodeError:
            return {'Issues': []}
    
    @staticmethod
    def run_golint(go_files):
        """Run golint for style checking."""
        results = []
        for file_path in go_files:
            cmd = ['golint', file_path]
            output = GoToolRunner.run_command(cmd)
            if output.strip():
                for line in output.splitlines():
                    results.append({
                        'file': file_path,
                        'message': line
                    })
        
        return results
    
    @staticmethod
    def run_gofmt(go_files):
        """Run gofmt to check formatting issues."""
        results = []
        for file_path in go_files:
            cmd = ['gofmt', '-d', file_path]
            output = GoToolRunner.run_command(cmd)
            if output.strip():
                results.append({
                    'file': file_path,
                    'diff': output
                })
        
        return results
    
    @staticmethod
    def run_go_test(repo_path):
        """Run go test with coverage."""
        # Create a temporary coverage file
        coverage_file = os.path.join(repo_path, 'coverage.out')
        
        # Run tests with coverage
        cmd = ['go', 'test', './...', '-coverprofile', coverage_file]
        GoToolRunner.run_command(cmd, cwd=repo_path, capture_output=False)
        
        # Parse coverage
        coverage_data = {}
        if os.path.exists(coverage_file):
            with open(coverage_file, 'r') as f:
                for line in f:
                    if line.startswith('mode:'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        file_path = parts[0]
                        coverage_info = parts[1]
                        coverage_data[file_path] = coverage_info
            
            # Clean up
            os.remove(coverage_file)
        
        return coverage_data
    
    @staticmethod
    def analyze_dependencies(repo_path):
        """Analyze Go module dependencies."""
        # Check if it's a Go module
        go_mod_path = os.path.join(repo_path, 'go.mod')
        if not os.path.exists(go_mod_path):
            return {'error': 'Not a Go module'}
        
        # Get dependencies
        cmd = ['go', 'list', '-m', 'all']
        output = GoToolRunner.run_command(cmd, cwd=repo_path)
        
        dependencies = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 1 and parts[0] != 'go':
                dep = {'name': parts[0]}
                if len(parts) >= 2:
                    dep['version'] = parts[1]
                dependencies.append(dep)
        
        # Check for outdated dependencies
        cmd = ['go', 'list', '-u', '-m', 'all']
        output = GoToolRunner.run_command(cmd, cwd=repo_path)
        
        outdated = []
        for line in output.splitlines():
            if '[' in line and ']' in line:  # Contains update information
                parts = line.split()
                name = parts[0]
                current_version = parts[1] if len(parts) > 1 else ''
                update_info = line[line.find('['):line.find(']')+1]
                outdated.append({
                    'name': name,
                    'current_version': current_version,
                    'update_info': update_info
                })
        
        return {
            'dependencies': dependencies,
            'outdated': outdated
        }