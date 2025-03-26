import pytest
import sys
import os

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/"])
    # Add command line arguments for more flexibility
    
    def run_tests():
        args = ["-v"]
        
        # Allow for test directory override
        test_path = os.getenv("TEST_PATH", "src/tests/")
        
        # Add common pytest options
        args.extend([
            "--capture=no",  # Show print statements
            "--tb=short",    # Shorter traceback format
            "-ra",          # Show extra test summary
            "--maxfail=5",  # Stop after 5 failures
            "--durations=3" # Show 3 slowest tests
        ])

        # Add custom markers if provided
        if len(sys.argv) > 1:
            args.extend(sys.argv[1:])
            
        args.append(test_path)
        return pytest.main(args)

    sys.exit(run_tests())