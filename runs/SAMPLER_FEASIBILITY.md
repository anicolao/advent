# Christmas sampler trial

The user rejected the landscape compositions because individual 9×9 days were often blank or meaningless fragments. Two new sources were generated with the built-in image-generation tool, requesting a 5×5 sampler of independent Christmas motifs. Exact prompts: [ClickArt](../inputs/clickart-sampler-prompt.txt), [FriXion](../inputs/frixion-sampler-prompt.txt). Generated sources are saved alongside them.

The preferred new outputs are `clickart-sampler-nearest` and `frixion-sampler-nearest`. Their full previews are exact 20× enlargements of the 45×45 artwork; `daily-preview.png` separates the 25 exact tiles for individual inspection. Earlier landscapes and BOX sampler conversions remain available for comparison.

| Run | Fewest distinct colours in any day | Fewest colours occupying 3+ cells | Largest single-colour share in any day |
| --- | --- | --- | --- |
| clickart / christmas | 1 | 1 | 100.0% |
| clickart / sampler | 4 | 2 | 72.8% |
| clickart / sampler-nearest | 3 | 2 | 90.1% |
| frixion / christmas | 1 | 1 | 100.0% |
| frixion / sampler | 3 | 3 | 77.8% |
| frixion / sampler-nearest | 3 | 3 | 80.2% |

Nearest-neighbour sampling avoids averaging colours across icon boundaries. It gives cleaner silhouettes than BOX on these sources, but can discard narrow details. Neither method guarantees an interesting day: several sources have insufficient foreground/background contrast, notably the white ClickArt snowman on white and the red FriXion stocking on red. Those shortcomings remain visible in the exported tiles. The original prompt requested four substantial colours and limited background coverage; the generated output did not consistently meet those requests. Counts are reported honestly rather than treated as passed art requirements.

The sampler makes the daily activity substantially more varied than the landscape. Gifts, bells, wreaths, mugs, and several other simple silhouettes survive better than faces or intricate decorations. Recognisability still requires the user's judgement, and the 9×9 limit favours very simple motifs. No manual pixel edits were applied.

Both preferred mosaics pass canonical geometry, palette, tile reassembly, inventory, preview, and deterministic conversion validation. Six implementation tests pass, including saved nearest-sampling validation. Colour-variety reports are diagnostics, not proof of physical feasibility or recognition.
