# AssemblMe

AssemblMe is a Blender addon for creating assembly and disassembly animations from finished object layouts. It is built for LEGO, Bricker, LDraw, and other model workflows where every part already has a final resting place and you want to generate clean build motion without hand-keyframing every object.

Current addon version: `2.0.0`

Blender target: `5.0+`

## What It Does

- Animates objects into or out of their final positions.
- Builds by layer height or by Bricker/LDraw-style step data.
- Supports instruction-style reveals, submodel/bag grouping, and final hero connection moments.
- Lets parts follow a selected Blender curve for more directed motion.
- Keeps animations editable and repeatable through named animation entries.
- Includes practical presets for common assembly looks.

## Quick Start

1. Install and enable the addon in Blender.
2. Open the `AssemblMe` tab in the 3D View sidebar.
3. Add a new animation entry.
4. Choose a collection, or select objects and click `From Selection`.
5. Pick a preset or adjust the settings manually.
6. Click `Create Build Animation`.
7. Change settings any time and click `Update Build Animation`.

Use `Start Over` to clear an existing AssemblMe animation before removing that animation entry.

## Core Workflow

AssemblMe works from a final model state. Put your bricks or objects where they should end up, then AssemblMe creates the motion that brings them there or pulls them away.

The main panels are:

- `Animations`: manage one or more animation entries and choose the collection to animate.
- `Actions`: create, update, or clear the generated build animation.
- `Settings`: control timing, ordering, movement, curve following, and build direction.
- `Visualizer Settings`: adjust the layer visualizer.
- `Preset Manager`: save, restore, or remove presets.

## Presets

Default presets live in `lib/default_presets`.

- `standard_build`: a clean upward build.
- `Rain`: pieces drop in from above with bounce-style interpolation.
- `Fly-In`: pieces fly in with randomized position and rotation.
- `Explode`: disassembly-style burst outward.
- `Step-by-Step`: slower instruction-like stepping.
- `follow_curve`: baseline settings for curve-guided motion.

Presets are just starting points. After choosing one, adjust the settings and update the animation.

## Build Ordering

AssemblMe has two ordering modes:

- `Layer Height`: the classic AssemblMe mode. Objects are grouped by their position along the layer orientation.
- `Build Order`: uses Bricker/LDraw-style step data when available.

Build Order mode can group by:

- `Steps`: animate each instruction step.
- `Submodels`: reveal each submodel or bag-like collection.
- `Submodel Steps`: animate steps within each submodel.

`Hero Final` splits the last few objects into one-by-one final connection moments. This is useful for social clips where the final snap should feel intentional.

If no build-order data is found, `Fallback to Layers` lets AssemblMe use layer height instead.

## Follow Curve

To make parts follow a path:

1. Create or select a Blender curve.
2. In AssemblMe settings, assign it in `Curve Path`.
3. Create or update the animation.

When a valid curve is selected, AssemblMe uses it automatically. The curve's endpoint acts as the landing anchor, so every object follows the same curve shape while still ending at its own final position.

Notes:

- The path object must be a Blender `Curve`.
- The curve needs at least two usable points.
- Location/rotation offset controls are hidden while curve following is active because the curve controls the travel path.

## Important Settings

- `Start`: first frame of the animation.
- `Step`: frame gap between each layer, step, or group.
- `Velocity`: how quickly each object travels between its start and final location.
- `Order`: choose layer-based or build-order timing.
- `Curve Path`: optional curve object for path-following motion.
- `Layer Orientation`: direction used for layer-height sorting.
- `Layer Height`: size of each layer slice.
- `Build Type`: assemble or disassemble.
- `Inverted Build`: reverse the layer/build direction.
- `Skip Empty Selections`: avoid timing gaps from empty layers.
- `Use Global`: apply offsets in world space.
- `Mesh Objects Only`: ignore non-mesh objects.

## Working With LEGO Models

For Bricker or LDraw imports, place the final model exactly as you want it to appear. If the model contains step, submodel, bag, or compatible custom metadata, Build Order mode can use it for more instruction-like animation. If the metadata is missing, use Layer Height mode or enable fallback.

Useful custom object properties for build-order fallback include:

- `assemblme_step`
- `bricker_step`
- `step_num`
- `step`
- `ldraw_step`
- `assemblme_submodel`
- `bricker_submodel`
- `submodel_name`
- `submodel`
- `bag`

## Troubleshooting

If no animation is created:

- Make sure the animation entry has a collection.
- Make sure the collection contains objects.
- If `Mesh Objects Only` is enabled, make sure the collection contains mesh objects.
- If Build Order mode is enabled, try enabling `Fallback to Layers`.

If Follow Curve does not work:

- Make sure `Curve Path` points to a Blender curve object.
- Make sure the curve has at least two points.
- Re-run `Create Build Animation` or `Update Build Animation` after selecting the curve.

If presets look stale or broken:

- Use the default presets listed above.
- Avoid old copied presets from previous experimental builds.
- Restore presets from the Preset Manager if needed.

## Support

AssemblMe is available on the [Blender Market](https://www.blendermarket.com/products/assemblme). Purchasing a license supports development and includes customer support.

Issues and development tracking live on GitHub:

https://github.com/bblanimation/assemblme/issues

## Contributing

Contributions are welcome. Fork the repository, make focused changes, and submit a pull request. Good contributions are usually small, testable, and aligned with the addon goal: faster, clearer, more controllable assembly animation.

## License

AssemblMe is distributed under the GNU General Public License v3. See `LICENSE` for details.
