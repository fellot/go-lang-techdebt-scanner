"""
Report Generator

Generates a comprehensive technical debt report.
"""

import os
import datetime
from scoring.thresholds import DebtThresholds

class ReportGenerator:
    """Generates technical debt reports."""
    
    def __init__(self, config):
        """Initialize the report generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.thresholds = DebtThresholds(config)
    
    def generate(self, results, output_path):
        """Generate a technical debt report.
        
        Args:
            results: Dictionary with scan results
            output_path: Path to write the report
        """
        # Create report content
        report = self._create_report(results)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(report)
    
    def _create_report(self, results):
        """Create the report content.
        
        Args:
            results: Dictionary with scan results
            
        Returns:
            String with the report content
        """
        repo_path = results['repo_path']
        overall_score = results['overall_score']
        category_scores = results['category_scores']
        metrics = results['metrics']
        
        # Determine overall debt level
        overall_level = self.thresholds.get_debt_level(overall_score)
        
        # Create report header
        report = [
            "# Technical Debt Report",
            f"Repository: {os.path.basename(repo_path)}",
            f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Overall Debt Score: {overall_score:.2f}/100 ({overall_level.upper()})",
            "",
            "## Summary",
            "",
            "| Category | Score | Level |",
            "| -------- | ----- | ----- |",
        ]
        
        # Add category summaries
        for category, score in category_scores.items():
            level = self.thresholds.get_debt_level(score)
            report.append(f"| {category.replace('_', ' ').title()} | {score:.2f} | {level.upper()} |")
        
        report.append("")
        
        # Add detailed sections for each category
        report.extend(self._create_complexity_section(metrics['complexity']))
        report.extend(self._create_duplication_section(metrics['duplication']))
        report.extend(self._create_test_quality_section(metrics['test_quality']))
        report.extend(self._create_dependencies_section(metrics['dependencies']))
        report.extend(self._create_churn_section(metrics['churn']))
        report.extend(self._create_readability_section(metrics['readability']))
        
        # Add recommendations
        report.extend(self._create_recommendations(results))
        
        return "\n".join(report)
    
    def _create_complexity_section(self, complexity_metrics):
        """Create the complexity section of the report."""
        section = [
            "## Code Complexity",
            "",
            f"Overall Complexity Score: {complexity_metrics['overall_score']:.2f}/100",
            "",
            "### Cyclomatic Complexity",
            f"- Average: {complexity_metrics['cyclomatic']['average']:.2f}",
            f"- Functions exceeding threshold: {complexity_metrics['cyclomatic']['violations']}",
            "",
            "#### Top Offenders:",
            ""
        ]
        
        for offender in complexity_metrics['cyclomatic']['worst_offenders']:
            section.append(f"- {offender['file_info']} (Complexity: {offender['complexity']})")
        
        section.extend([
            "",
            "### Cognitive Complexity",
            f"- Average: {complexity_metrics['cognitive']['average']:.2f}",
            f"- Functions exceeding threshold: {complexity_metrics['cognitive']['violations']}",
            "",
            "#### Top Offenders:",
            ""
        ])
        
        for offender in complexity_metrics['cognitive']['worst_offenders']:
            section.append(f"- {offender['file_info']} (Complexity: {offender['complexity']})")
        
        section.append("")
        return section
    
    def _create_duplication_section(self, duplication_metrics):
        """Create the duplication section of the report."""
        section = [
            "## Code Duplication",
            "",
            f"Duplication Score: {duplication_metrics['score']:.2f}/100",
            f"- Total lines of code: {duplication_metrics['total_lines']}",
            f"- Duplicated lines: {duplication_metrics['duplicated_lines']}",
            f"- Duplication percentage: {duplication_metrics['duplication_percentage']:.2f}%",
            "",
            "### Files with Highest Duplication:",
            ""
        ]
        
        for file_info in duplication_metrics['files_with_duplication']:
            section.append(
                f"- {file_info['file']} ({file_info['duplicated_lines']} lines, "
                f"{file_info['percentage']:.2f}%)"
            )
        
        section.append("")
        return section
    
    def _create_test_quality_section(self, test_metrics):
        """Create the test quality section of the report."""
        section = [
            "## Test Quality",
            "",
            f"Test Quality Score: {test_metrics['overall_score']:.2f}/100",
            f"- Test files: {test_metrics['test_file_count']}",
            f"- Files with tests: {test_metrics['files_with_tests']}",
            f"- Files without tests: {test_metrics['files_without_tests']}",
            f"- Average coverage: {test_metrics['average_coverage']:.2f}%",
            f"- Test-to-code ratio: {test_metrics['test_to_code_ratio']:.2f}",
            "",
            "### Files Without Tests:",
            ""
        ]
        
        for file_path in test_metrics['uncovered_files'][:10]:  # Show top 10
            section.append(f"- {file_path}")
        
        section.append("")
        return section
    
    def _create_dependencies_section(self, dependency_metrics):
        """Create the dependencies section of the report."""
        section = [
            "## Dependency Health",
            "",
            f"Dependency Health Score: {dependency_metrics['score']:.2f}/100",
        ]
        
        if not dependency_metrics['is_module']:
            section.append("- Not a Go module")
            return section
        
        section.extend([
            f"- Total dependencies: {dependency_metrics['dependency_count']}",
            f"- Outdated dependencies: {dependency_metrics['outdated_count']} "
            f"({dependency_metrics['outdated_percentage']:.2f}%)",
            f"- Vulnerable dependencies: {dependency_metrics['vulnerable_count']}",
            "",
            "### Outdated Dependencies:",
            ""
        ])
        
        for dep in dependency_metrics['outdated_dependencies']:
            section.append(f"- {dep['name']} {dep['current_version']} {dep['update_info']}")
        
        if dependency_metrics['vulnerable_count'] > 0:
            section.extend([
                "",
                "### Vulnerable Dependencies:",
                ""
            ])
            
            for dep in dependency_metrics['vulnerable_dependencies']:
                section.append(f"- {dep}")
        
        section.append("")
        return section
    
    def _create_churn_section(self, churn_metrics):
        """Create the churn section of the report."""
        section = [
            "## Code Churn and Stability",
            "",
            f"Churn Score: {churn_metrics['score']:.2f}/100",
            f"- Average churn rate: {churn_metrics['average_churn_rate']:.2f} lines per commit",
            f"- Total commits: {churn_metrics['repository_churn']['commit_count']}",
            f"- Total additions: {churn_metrics['repository_churn']['total_additions']}",
            f"- Total deletions: {churn_metrics['repository_churn']['total_deletions']}",
            "",
            "### Files with Highest Churn:",
            ""
        ]
        
        for file_info in churn_metrics['high_churn_files']:
            section.append(
                f"- {file_info['file']} (Churn rate: {file_info['churn_rate']:.2f}, "
                f"Commits: {file_info['commits']})"
            )
        
        section.append("")
        return section
    
    def _create_readability_section(self, readability_metrics):
        """Create the readability section of the report."""
        section = [
            "## Code Readability and Maintainability",
            "",
            f"Readability Score: {readability_metrics['score']:.2f}/100",
            f"- Lint issues: {readability_metrics['lint_issues']}",
            f"- Formatting issues: {readability_metrics['fmt_issues']}",
            f"- Average comment ratio: {readability_metrics['avg_comment_ratio']:.2f}",
            f"- Average function length: {readability_metrics['avg_function_length']:.2f} lines",
            "",
            "### Files with Readability Issues:",
            ""
        ]
        
        # Sort files by various metrics to find those with readability issues
        problematic_files = sorted(
            readability_metrics['file_metrics'],
            key=lambda x: (
                -x['avg_function_length'],  # Longer functions first
                x['comment_ratio']  # Lower comment ratio first
            )
        )[:10]  # Top 10
        
        for file_info in problematic_files:
            section.append(
                f"- {file_info['file']} (Avg function length: {file_info['avg_function_length']:.2f}, "
                f"Comment ratio: {file_info['comment_ratio']:.2f})"
            )
        
        section.append("")
        return section
    
    def _create_recommendations(self, results):
        """Create recommendations based on scan results."""
        metrics = results['metrics']
        category_scores = results['category_scores']
        
        # Find the worst categories
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        section = [
            "## Recommendations",
            ""
        ]
        
        # Add recommendations for the top 3 worst categories
        for category, score in sorted_categories[:3]:
            if category == 'complexity' and score > self.thresholds.thresholds['medium']:
                section.extend([
                    "### Reduce Code Complexity",
                    "",
                    "- Refactor functions with high cyclomatic complexity",
                    "- Break down large functions into smaller, more focused ones",
                    "- Simplify nested conditionals and loops",
                    "- Consider using design patterns to simplify complex logic",
                    ""
                ])
            
            elif category == 'duplication' and score > self.thresholds.thresholds['medium']:
                section.extend([
                    "### Reduce Code Duplication",
                    "",
                    "- Extract duplicated code into reusable functions or methods",
                    "- Create utility packages for common functionality",
                    "- Apply DRY (Don't Repeat Yourself) principles",
                    "- Consider using code generation for repetitive patterns",
                    ""
                ])
            
            elif category == 'test_quality' and score > self.thresholds.thresholds['medium']:
                section.extend([
                    "### Improve Test Quality",
                    "",
                    "- Add tests for uncovered files and functions",
                    "- Increase test coverage for critical components",
                    "- Implement table-driven tests for better coverage",
                    "- Add integration and end-to-end tests",
                    "- Use test-driven development (TDD) for new features",
                    ""
                ])
            
            elif category == 'dependencies' and score > self.thresholds.thresholds['medium']:
                section.extend([
                    "### Improve Dependency Health",
                    "",
                    "- Update outdated dependencies",
                    "- Fix vulnerable dependencies immediately",
                    "- Implement dependency scanning in CI/CD pipeline",
                    "- Consider using dependency management tools",
                    "- Regularly audit and prune unnecessary dependencies",
                    ""
                ])
            
            elif category == 'churn' and score > self.thresholds.thresholds['medium']:
                section.extend([
                    "### Reduce Code Churn",
                    "",
                    "- Stabilize frequently changing files",
                    "- Improve test coverage for high-churn files",
                    "- Review and refactor hotspots",
                    "- Consider breaking down large, frequently changed files",
                    "- Implement more thorough code reviews for high-churn areas",
                    ""
                ])
            
            elif category == 'readability' and score > self.thresholds.thresholds['medium']:
                section.extend([
                    "### Improve Code Readability",
                    "",
                    "- Fix linting and formatting issues",
                    "- Add meaningful comments and documentation",
                    "- Break down long functions",
                    "- Use descriptive variable and function names",
                    "- Follow Go style guidelines and best practices",
                    "- Run gofmt and golint as part of your workflow",
                    ""
                ])
        
        return section