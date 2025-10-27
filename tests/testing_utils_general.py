# coding=utf-8
import os


def is_run_on_a_teamcity_continuous_integration_server() -> bool:
    """
    Check if python is executed in the continuous integration server.

    Note: The check is specific to TeamCity server
    """
    try:
        import teamcity as tc

        # Note: if it return 'LOCAL' then it is not running on a TeamCity server
        tc_version = os.getenv("TEAMCITY_VERSION")

        if tc_version != "LOCAL":
            print(f"is running under teamcity TEAMCITY_VERSION={tc_version}")
            return True
        else:
            print(
                f"TEAMCITY_VERSION={tc_version} ››› run not executed on CI server"
            )
            return False
    except ImportError:
        print("python is not executed on CI server")
        return False
