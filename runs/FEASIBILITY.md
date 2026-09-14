# First Christmas mosaic trial

Two sources were independently generated with the built-in image-generation tool, using the same Christmas tree/cabin brief and each set's photographed palette. Exact prompts are in [ClickArt](../inputs/clickart-prompt.txt) and [FriXion](../inputs/frixion-prompt.txt). Source images and generation metadata are preserved alongside them. Model, seed, and generation cost were not exposed and are recorded as unknown.

| Result | ClickArt | FriXion |
| --- | --- | --- |
| Canonical dimensions | 45×45 | 45×45 |
| Allowed/used colours, including white | 13/13 | 13/13 |
| Filled positions | 2,025 | 2,025 |
| Tile patterns | 25 at 9×9 | 25 at 9×9 |
| Artifact validation and deterministic reconversion | Passed | Passed |

Both use the specified BOX downsampling followed by nearest colour in encoded sRGB, without dithering or manual pixel edits. Sources remain independent compositions, so this is not a controlled comparison of palettes using identical artwork.

Visual inspection by the coding assistant: both retain a decorated tree, star, cabin, and snowy ground. ClickArt produces a dark night scene and FriXion a brighter scene with white garlands. Small window divisions are lost. Averaged boundary colours sometimes map to unrelated palette colours: ClickArt has pink pixels around snowy roof edges and smoke, and FriXion has cyan/pink pixels along snow boundaries. Small sky stars also shift colour. These are baseline conversion artifacts, not additional colours outside the palette.

These artifacts are retained for the user's feasibility judgement. If they prove distracting, a follow-up experiment could compare a perceptual colour distance or majority-colour downsampling against this saved baseline. No alternative algorithm has been applied to these outputs.

Five automated test cases pass, covering exact palette assignment, tie-breaking, invalid palettes, transparency, dimensions/cropping, EXIF orientation, animated-input rejection, asymmetric tile assembly, overwrite rejection, tamper detection, and repeatability.

Human recognition scoring and a guided 81-position assembly trial have **not** been performed. The automated results establish geometric and palette correctness, not full physical feasibility. Colours still represent photographed marker plastic, pending confirmation against ink on paper.
