

from __future__ import annotations

from pathlib import Path
from config_validator.core.validator import ValidationSession
from config_validator.core.config import ValidationConfig
from config_validator.storage.local_strategy import LocalStrategy
from config_validator.plugins.check_env import EnvValueNotEmpty




# # def test_validate_happy_path(tmp_path: Path) -> None:
# #     f = tmp_path / "svc.yaml"
# #     f.write_text(
# #         """
# #         service: user-api
# #         replicas: 3
# #         image: myregistry.com/user-api:1.4.2
# #         env:
# #             DATABASE_URL: postgres://db:5432/x
# #             REDIS_URL: redis://cache:6379
# #         """,
# #         encoding="utf-8",
# #         )


# #     res = validate_file(f)
# #     assert res["valid"] is True
# #     assert res["errors"] == []
# #     assert res["registry"] == "myregistry.com"



# def test_validate_core_replicas(tmp_path: Path) -> None:
#     f = tmp_path / "bad.yaml"
#     f.write_text(
#         """
#         service: user-api
#         replicas: 1000
#         image: myregistry.com/user-api:1.0.0
#         env:
#             DATABASE_URL: "test"
#             REDIS_URL: redis://cache:6379
#         """,
#         encoding="utf-8",
#         )


#     res = validate_file(f)
#     assert res["valid"] is False
#     # should include replicas range, image format, env uppercase errors
#     joined = "\n".join(res["errors"]) # simpler assertion
#     print("joined",joined)
#     errors= res.get("errors",[])
#     print("**********************************************")
#     print("errors",errors)
#     print("**********************************************")
#     assert "replicas must be an integer between 1 and 10" in errors
     
 
# def test_validate_core_goodreplicas(tmp_path: Path) -> None:
#     f = tmp_path / "good.yaml"
#     f.write_text(
#         """
#         service: user-api
#         replicas: 5
#         image: myregistry.com/user-api:1.0.0
#         env:
#             DATABASE_URL: "test"
#             REDIS_URL: redis://cache:6379
#         """,
#         encoding="utf-8",
#         )


#     res = validate_file(f)
#     assert res["valid"] is True
#     # should include replicas range, image format, env uppercase errors
#     joined = "\n".join(res["errors"]) # simpler assertion
#     print("joined",joined)
#     errors= res.get("errors",[])
#     print("**********************************************")
#     print("errors",errors)
#     print("**********************************************")
#     assert "replicas must be an integer between 1 and 10" not in errors    
# # def test_validate_core_errors(tmp_path: Path) -> None:
# #     f = tmp_path / "bad.yaml"
# #     f.write_text(
# #         """
# #         service: user-api
# #         replicas: 2
# #         image: myregistry.com/user-api:1.0.0
# #         env:
# #             DATABASE_URL: ""
# #             REDIS_URL: redis://cache:6379
# #         """,
# #         encoding="utf-8",
# #         )


# #     res = validate_file(f)
# #     assert res["valid"] is False
# #     # should include replicas range, image format, env uppercase errors
# #     joined = "\n".join(res["errors"]) # simpler assertion
    
    
# #     assert "env values must be non-empty" in joined
     
# #     # assert "replicas must be an integer" in joined
# #     # assert "image must match <registry>/<service>:<version>" in joined
# #     # assert "env keys must be UPPERCASE" in joined


def test_plugin_env_value_not_empty(tmp_path: Path) -> None:
    """Test that the EnvValueNotEmpty plugin correctly identifies empty env values."""
    f = tmp_path / "svc.yaml"
    f.write_text(
        """
        service: user-api
        replicas: 2
        image: myregistry.com/user-api:1.0.0
        env:
            DATABASE_URL: ""
            REDIS_URL: redis://cache:6379
        """,
        encoding="utf-8",
        )

    # Create test configuration and storage strategy
    config = ValidationConfig()
    storage = LocalStrategy({"base_path": str(tmp_path)})
    session = ValidationSession(config, storage)

    res = session.validate_file(str(f))
    assert res["valid"] is False
    # plugin should flag DATABASE_URL as empty
    assert any("env values must be non-empty strings" in e for e in res["errors"])


def test_plugin_env_value_valid(tmp_path: Path) -> None:
    """Test that the EnvValueNotEmpty plugin passes valid env values."""
    f = tmp_path / "svc.yaml"
    f.write_text(
        """
        service: user-api
        replicas: 2
        image: myregistry.com/user-api:1.0.0
        env:
            DATABASE_URL: "postgres://db:5432/x"
            REDIS_URL: "redis://cache:6379"
        """,
        encoding="utf-8",
        )

    # Create test configuration and storage strategy
    config = ValidationConfig()
    storage = LocalStrategy({"base_path": str(tmp_path)})
    session = ValidationSession(config, storage)

    res = session.validate_file(str(f))
    # Should be valid since all env values are non-empty
    assert res["valid"] is True
    assert not any("env values must be non-empty strings" in e for e in res["errors"])




# # def test_plugin_env_value_not_empty(tmp_path: Path) -> None:
# #     f = tmp_path / "svc.yaml"
# #     f.write_text(
# #         """
# #         service: user-api
# #         replicas: 2
# #         image: myregistry.com/user-api:1.0.0
# #         env:
# #             DATABASE_URL: ""
# #             REDIS_URL: redis://cache:6379
# #         """,
# #         encoding="utf-8",
# #         )


# #     res = validate_file(f)
# #     assert res["valid"] is False
# #     # plugin should flag DATABASE_URL as empty
# #     assert any("env values must be non-empty strings" in e for e in res["errors"]) # plugin hit