# README

Blender add-on for automated generation of LEGO Brick Build animation (Blender version: 2.78b)

## LEGO Frame-by-Frame Build Add-On:
  * Features:
      * Customizable layer size and orientation, build speed, brick velocity, and more.
      * LEGO bricks can be assembled or disassembled
      * LEGO brick location and rotation offset can be customized and/or randomized
      * Convenient button for checking build animation duration before creating it
      * Convenient 'Start Over' button to clear generated animation
      * Auto-saves backup file before generating or deleting generated animation
  * Instructions:
      * Begin by selecting all LEGO bricks for which you wish to generate build (cameras, lights, and plain axes are ignored)
      * Adjust animation settings to desired values
      * Click 'Create Build Animation' (may take a few minutes; you can monitor progress in the terminal)
      * If the animation settings were not to your liking, click 'Start Over' and repeat previous steps
      * NOTE: Once an animation has been generated, the objects in the animation should only be controlled by their automatically generated 'PLAIN_AXES' parent object. If objects are moved or keyframes are added, these changes will be cleared by the 'Start Over' button.
  * Future improvements:
      * Improve calculations for layer orientation to improve visualization accuracy
      * Don't perform unnecessary keyframing in 'Update Build Animation' function
          * If start, step, velocity, layer height, build type, assemble from other direction, layer orientation, and skip empty selection haven't been changed, no need to insert first frame
          * If all in first bullet point and location offset haven't changed, don't insert location keyframes
          * If all in first bullet point and rotation offset haven't changed, don't insert rotation keyframes
      * Break files down
      * Clean and improve code readability`
