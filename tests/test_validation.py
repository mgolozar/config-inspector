from __future__ import annotations


from pathlib import Path


from config_validator.core.validator import validate_file




# def test_validate_happy_path(tmp_path: Path) -> None:
#     f = tmp_path / "svc.yaml"
#     f.write_text(
#         """
#         service: user-api
#         replicas: 3
#         image: myregistry.com/user-api:1.4.2
#         env:
#             DATABASE_URL: postgres://db:5432/x
#             REDIS_URL: redis://cache:6379
#         """,
#         encoding="utf-8",
#         )


#     res = validate_file(f)
#     assert res["valid"] is True
#     assert res["errors"] == []
#     assert res["registry"] == "myregistry.com"


 
def test_validate_core_errors(tmp_path: Path) -> None:
    f = tmp_path / "bad.yaml"
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


    res = validate_file(f)
     
    assert res["valid"] is False
    # should include replicas range, image format, env uppercase errors
    joined = "\n".join(res["errors"]) # simpler assertion
    print("joined",joined)
    errors= res.get("errors",[])
    # print("**********************************************")

    # print("valid",res["valid"])
    # print("errors",errors)
    # print("**********************************************")
     
    # print("errors",joined)
    # print("env values must be non-empty" in joined)

    # print("cccccc*****************************************")
    assert "env values must be non-empty" in joined
  