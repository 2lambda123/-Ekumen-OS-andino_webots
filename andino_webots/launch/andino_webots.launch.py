# BSD 3-Clause License

# Copyright (c) 2023, Ekumen Inc.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import launch
import os
import pathlib
import xacro

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.substitutions.path_join_substitution import PathJoinSubstitution
from webots_ros2_driver.urdf_spawner import URDFSpawner
from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController

# Obtain packages
curr_pkg_dir = get_package_share_directory('andino_webots')
andino_gazebo_pkg_dir = get_package_share_directory('andino_gazebo')

def generate_launch_description():

    andino_gazebo_xacro_path = os.path.join(andino_gazebo_pkg_dir, 'urdf', 'andino.gazebo.xacro')
    andino_gazebo_description = xacro.process_file(andino_gazebo_xacro_path, mappings={'use_gazebo_ros_control': 'False', 'use_fixed_caster': "False"}).toprettyxml(indent='    ')

    world = LaunchConfiguration('world')

    world_argument = DeclareLaunchArgument(
        'world',
        default_value='andino_webots.wbt',
    )
    # The WebotsLauncher is used to start a Webots instance.
    # Arguments:
    # - `world` (str):              Path to the world to launch.
    # - `gui` (bool):               Whether to display GUI or not.
    # - `mode` (str):               Can be `pause`, `realtime`, or `fast`.
    # - `ros2_supervisor` (bool):   Spawn the `Ros2Supervisor` custom node that communicates with a Supervisor robot in the simulation.
    webots = WebotsLauncher(
        world=PathJoinSubstitution([curr_pkg_dir, 'worlds', world]),
        ros2_supervisor=True
    )

    # webots_ros2 node to spawn robots from URDF
    # TODO Update to PROTOSpawner when implementation is released
    spawn_andino = URDFSpawner(
        name='andino',
        robot_description=andino_gazebo_description,
        translation='0 0 0.022',
        rotation=' 0 0 1 0',
    )

    # Standard ROS 2 launch description
    return launch.LaunchDescription([
        # Set the world argument
        world_argument,
        # Start the Webots node
        webots,
        # Starts the Ros2Supervisor node created with the WebotsLauncher
        webots._supervisor,
        # Spawn Noah's URDF
        spawn_andino,
        # This action will kill all nodes once the Webots simulation has exited
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
            )
        )
    ])