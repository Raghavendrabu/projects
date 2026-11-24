import os
import sys
import pytest
import importlib.util

def main():
    print("\n" + "="*60)
    print("[START] GMInsta Selenium Automated Test Suite Runner")
    print("="*60)

    # Resolve paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    screenshots_dir = os.path.join(base_dir, "screenshots")
    reports_dir = os.path.join(base_dir, "reports")
    report_file = os.path.join(reports_dir, "report.html")

    # Create directories
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    print(f"[DIR] Created/verified screenshots directory: {screenshots_dir}")
    print(f"[DIR] Created/verified reports directory: {reports_dir}")

    # Build pytest arguments
    # Headless mode is disabled by default
    pytest_args = [
        base_dir,
        "-v"
    ]

    # Detect if pytest-html is installed
    has_html_plugin = importlib.util.find_spec("pytest_html") is not None
    if has_html_plugin:
        print("[REPORT] Found pytest-html plugin. Enabling HTML reports.")
        pytest_args.extend([
            f"--html={report_file}",
            "--self-contained-html"
        ])
    else:
        print("[TIP] Hint: Run 'pip install pytest-html' to generate beautiful visual reports.")

    # Check for CLI override to run browser in headless mode
    if "--headless" in sys.argv:
        pytest_args.append("--headless")
        print("[INFO] Headless mode enabled. Browser will run in the background.")
    else:
        print("[INFO] Headless mode disabled. Browser window will be visible.")
    
    # Check if a specific browser is requested
    browser_index = -1
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--browser="):
            browser_index = i
            break
    if browser_index != -1:
        pytest_args.append(sys.argv[browser_index])
    else:
        # Default to chrome
        pytest_args.append("--browser=chrome")

    print(f"[RUN] Running pytest with arguments: {pytest_args}\n")
    
    # Run pytest
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "="*60)
    if exit_code == 0:
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"[FAIL] TEST SUITE FAILED WITH EXIT CODE: {exit_code}")
        print(f"[SCREENSHOT] Failed test screenshots can be found in: {screenshots_dir}")
    
    if has_html_plugin and os.path.exists(report_file):
        print(f"[REPORT] HTML Report generated at: {report_file}")
    print("="*60 + "\n")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
