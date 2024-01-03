# tmunlimiter_blender_plugin
An official plugin for Blender that allows users to create custom blocks for TMUnlimiter 2.0 and export them in GBX format.

## Features
- Support for ``Classic`` and ``Road`` block types.
- Support for ``Start``, ``Checkpoint``, ``Finish`` and ``StartFinish`` waypoint blocks.
- Support for ground and air block variations
- Support for game materials from all united environments
- Custom texture support
    - Texture filtering
    - Texture addressing
    - Texture type support:
        - ``Diffuse``
        - ``Specular``
        - ``Normal``
        - ``Lighting``
        - ``Occlusion``
- Custom ground and air spawn location support
- ``Point`` and ``Spot`` lighting

## Installation
### Before installation
You have to install ``python-lzo`` library required by the plugin.

#### Linux
Linux users can install ``python-lzo`` library using ``pip``.

Alternatively, you can install ``python-lzo`` using Blender's console by typing following code:

```python
import pip
pip.main(["install", "python-lzo"])
```

#### Windows
Official installation of the ``python-lzo`` library using ``pip`` is complicated.
You have to install [...] from website [...], unpack the pyd file and move it to [...] folder.

### Install plugin
You can install this plugin by going to the ``Preferences > Add-ons`` and clicking ``Install...`` button and choosing the zip file found in the releases section.