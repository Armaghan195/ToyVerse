
import subprocess
import sys

def run_tests(args=None):

    cmd = ["python", "-m", "pytest"]

    if args:
        cmd.extend(args)
    else:
        cmd.extend(["-v", "--tb=short"])

    print("=" * 60)
    print("Running ToyVerse Backend Tests")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd, cwd=".")

    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Check output above.")
    print("=" * 60)

    return result.returncode

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    exit_code = run_tests(args)
    sys.exit(exit_code)
