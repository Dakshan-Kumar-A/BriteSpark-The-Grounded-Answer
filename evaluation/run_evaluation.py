import json

from src.main import (
    build_system,
    process_query,
)

from src.utils.session import (
    SessionMemory,
)


def main():

    with open(
        "evaluation/test_cases.json",
        encoding="utf-8",
    ) as file:

        tests = json.load(file)

    system = build_system()

    passed = 0
    total = len(tests)

    print(
        "\nEvaluation Results\n"
    )

    for index, test in enumerate(
        tests,
        start=1,
    ):

        memory = SessionMemory()

        result = process_query(
            test["question"],
            system,
            memory,
        )

        # ----------------------------------------------------
        # Normalize enum -> string
        # ----------------------------------------------------

        actual_status = (
            result.status.value
            if hasattr(
                result.status,
                "value"
            )
            else str(
                result.status
            )
        )

        expected_status = (
            test["expected_status"]
        )

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

        print()

    print(
        f"Final result: "
        f"{passed}/{total} passed"
    )


if __name__ == "__main__":
    main()