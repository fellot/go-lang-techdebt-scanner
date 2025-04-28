#!/usr/bin/env python3
"""
Go Technical Debt Scanner - CLI Entry Point
"""

import argparse
import os
import sys
import yaml
from scanner.repo_scanner import RepoScanner
from reporting.report_generator import ReportGenerator

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Go Technical Debt Scanner')
    parser.add_argument('repo_path', help='Path to the Go repository')
    parser.add_argument('--config', '-c', default='config.yaml', 
                        help='Path to configuration file')
    parser.add_argument('--output', '-o', default='debt_report.md',
                        help='Output report file path')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output in JSON format instead of Markdown')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_args()
    
    # Validate repository path
    if not os.path.isdir(args.repo_path):
        print(f"Error: {args.repo_path} is not a valid directory")
        sys.exit(1)
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize scanner
    scanner = RepoScanner(args.repo_path, config, verbose=args.verbose)
    
    # Run scan
    print(f"Scanning repository: {args.repo_path}")
    results = scanner.scan()
    
    if args.json:
        # Output JSON
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        # Generate Markdown report
        report_generator = ReportGenerator(config)
        report_generator.generate(results, args.output)
    
    print(f"Technical debt report generated: {args.output}")
    print(f"Overall debt score: {results['overall_score']:.2f}/100")
    
    # Print summary of debt categories
    print("\nDebt breakdown:")
    for category, score in results['category_scores'].items():
        level = "HIGH" if score > config['thresholds']['high'] else \
               "MEDIUM" if score > config['thresholds']['medium'] else "LOW"
        print(f"  {category}: {score:.2f}/100 ({level})")

if __name__ == "__main__":
    main()