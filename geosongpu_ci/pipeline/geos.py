from geosongpu_ci.utils.environment import Environment
from typing import Dict, Any
from geosongpu_ci.pipeline.task import TaskBase
from geosongpu_ci.utils.shell import shell_script
from geosongpu_ci.utils.registry import Registry
from geosongpu_ci.actions.pipeline import PipelineAction
from geosongpu_ci.actions.git import git_prelude
import datetime
import yaml


def _epilogue(env: Environment):
    # Export GEOS_INSTALL for future scripts
    env.set(
        "GEOS_INSTALL",
        f"{env.CI_WORKSPACE}/geos/install",
    )


def _check(env: Environment) -> bool:
    return env.exists("GEOS_INSTALL")


@Registry.register
class GEOS_NO_HYDROSTATIC(TaskBase):
    def run_action(
        self,
        config: Dict[str, Any],
        experiment_name: str,
        action: PipelineAction,
        env: Environment,
        metadata: Dict[str, Any],
    ):
        git_prelude(
            config,
            experiment_name,
            action,
            metadata,
            override_repo_name="geos",
            do_mepo=True,
        )

        # Build GEOS
        shell_script(
            name="build_geos",
            modules=[],
            env_to_source=[
                "geos/@env/g5_modules.sh",
            ],
            shell_commands=[
                "cd geos",
                "mkdir build",
                "cd build",
                f"export TMP={env.CI_WORKSPACE}/geos/build/tmp",
                "export TMPDIR=$TMP",
                "export TEMP=$TMP",
                "mkdir $TMP",
                "echo $TMP",
                "cmake .. -DBASEDIR=$BASEDIR/Linux -DCMAKE_Fortran_COMPILER=gfortran -DHYDROSTATIC=off -DCMAKE_INSTALL_PREFIX=../install",
                "make -j12 install",
            ],
        )

        _epilogue(env)

    def check(
        self,
        config: Dict[str, Any],
        experiment_name: str,
        action: PipelineAction,
        artifact_directory: str,
        env: Environment,
    ) -> bool:
        return _check(env)


@Registry.register
class GEOS(TaskBase):
    def run_action(
        self,
        config: Dict[str, Any],
        experiment_name: str,
        action: PipelineAction,
        env: Environment,
        metadata: Dict[str, Any],
    ):
        git_prelude(
            config,
            experiment_name,
            action,
            metadata,
            override_repo_name="geos",
            do_mepo=True,
        )

        # Build GEOS
        shell_script(
            name="build_geos",
            modules=[],
            env_to_source=[
                "geos/@env/g5_modules.sh",
            ],
            shell_commands=[
                "cd geos",
                "mkdir build",
                "cd build",
                f"export TMP={env.CI_WORKSPACE}/geos/build/tmp",
                "export TMPDIR=$TMP",
                "export TEMP=$TMP",
                "mkdir $TMP",
                "echo $TMP",
                "cmake .. -DBASEDIR=$BASEDIR/Linux -DCMAKE_Fortran_COMPILER=gfortran -DCMAKE_INSTALL_PREFIX=../install",
                "make -j12 install",
            ],
        )

        _epilogue(env)

    def check(
        self,
        config: Dict[str, Any],
        experiment_name: str,
        action: PipelineAction,
        artifact_directory: str,
        env: Environment,
    ) -> bool:
        return _check(env)
