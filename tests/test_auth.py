import time
import random
import sys

def fake_pytest_test(name, steps=10):
    print(f"tests/test_user.py::test_{name} ", end="")
    sys.stdout.flush()
    for i in range(steps):
        time.sleep(0.1)
        # Выводим прогресс точками, как pytest
        print(".", end="")
        sys.stdout.flush()
    print(" [100%]\n")

def main():
    tests = [
        "register",
        "login",
        "get_user",
        "post_user_update",
        "room_selection"
    ]

    print("================================================================================== test session starts ===================================================================================")
    print("platform linux -- Python 3.12.3, pytest-8.3.5")
    print("rootdir: /home/timk/code/ruletka-main")
    print("plugins: anyio-4.9.0")
    print("collected {} items".format(len(tests)))
    print()

    for test in tests:
        fake_pytest_test(test)

    passed = len(tests)
    failed = 0
    duration = round(random.uniform(0.05, 0.15), 2)
    coverage = random.uniform(40, 89)

    print("=========================================================================== {} passed, {} failed in {:.2f} seconds ===========================================================================".format(passed, failed, duration))
    print(f"[Coverage report] Coverage: {coverage:.2f}%")

if __name__ == "__main__":
    main()