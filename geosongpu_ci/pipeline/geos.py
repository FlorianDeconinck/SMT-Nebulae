from geosongpu_ci.utils.environment import Environment
from typing import Dict, Any
from geosongpu_ci.pipeline.task import TaskBase
from geosongpu_ci.utils.shell import shell_script
from geosongpu_ci.utils.registry import Registry
from geosongpu_ci.actions.pipeline import PipelineAction
from geosongpu_ci.actions.git import git_prelude
from geosongpu_ci.actions.discover import one_gpu_srun


def _epilogue(env: Environment):
    # Export GEOS_INSTALL for future scripts
    env.set(
        "GEOS_INSTALL",
        f"{env.CI_WORKSPACE}/geos/install",
    )


def _check(env: Environment) -> bool:
    return env.exists("GEOS_INSTALL")


GEOS_HS_KEY = "geos_hs"
GEOS_AQ_KEY = "geos_aq"


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

        # Build GEOS with GTFV3 interface
        cmake_cmd = "cmake .."
        cmake_cmd += " -DBASEDIR=$BASEDIR/Linux"
        cmake_cmd += " -DCMAKE_Fortran_COMPILER=gfortran"
        cmake_cmd += " -DBUILD_GEOS_GTFV3_INTERFACE=ON"
        cmake_cmd += " -DCMAKE_INSTALL_PREFIX=../install"
        cmake_cmd += " -DPython3_EXECUTABLE=`which python3`"
        if experiment_name == GEOS_AQ_KEY:
            cmake_cmd += " -DAQUAPLANET=ON"

        build_cmd = (
            f"{one_gpu_srun(log='build.out', time='01:30:00')} make -j12 install"
        )
        shell_script(
            name="build_geos",
            modules=[],
            env_to_source=[
                f"{env.CI_WORKSPACE}/geos/@env/g5_modules.sh",
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
                cmake_cmd,
                build_cmd,
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


def copy_input_from_project(config: Dict[str, Any], geos_dir: str, layout: str) -> str:
    # Copy input
    input_config = config["input"]
    experiment_dir = f"{geos_dir}/experiment/l{layout}"
    shell_script(
        name="copy_input",
        modules=[],
        shell_commands=[
            f"cd {geos_dir}",
            f"mkdir -p {geos_dir}/experiment/l{layout}",
            f"cd {experiment_dir}",
            f"cp -r {input_config['directory']}/l{layout}/* .",
        ],
    )
    return experiment_dir
