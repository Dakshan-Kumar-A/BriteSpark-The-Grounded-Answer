import json

from src.main import (
    build_system,
    process_query,
)

from src.utils.session import SessionMemory


def main():

    with open(
        "evaluation/test_cases.json",
        encoding="utf-8",
    ) as file:
        tests = json.load(file)

    system = build_system()

    passed = 0
    total = len(tests)

    print("\nEvaluation Results\n")

    for index, test in enumerate(
        tests,
        start=1,
    ):

        # Fresh memory for every independent test
        memory = SessionMemory()

        result = process_query(
            test["question"],
            system,
            memory,
        )

        # -------------------------------------------------
        # Normalize actual status
        # -------------------------------------------------

        actual_status = result.status

        if hasattr(
            actual_status,
            "value",
        ):
            actual_status = actual_status.value

        actual_status = str(
            actual_status
        ).strip().upper()

        # -------------------------------------------------
        # Normalize expected status
        # -------------------------------------------------

        expected_status = str(
            test["expected_status"]
        ).strip().upper()

        passed_test = (
            actual_status
            == expected_status
        )

        if passed_test:
            passed += 1
            label = "PASS"
        else:
            label = "FAIL"

        print(
            f"{index}. {label}"
        )

        print(
            f"Question: "
            f"{test['question']}"
        )

        print(
            f"Expected: "
            f"{expected_status}"
        )

        print(
            f"Actual: "
            f"{actual_status}"
        )

        # Show useful diagnostic information
        if not passed_test:

            print(
                f"Answer: "
                f"{result.answer}"
            )

            if result.reason:
                print(
                    f"Reason: "
                    f"{result.reason}"
                )

        print()

    print(
        f"Final result: "
        f"{passed}/{total} passed"
    )


if __name__ == "__main__":
    main()