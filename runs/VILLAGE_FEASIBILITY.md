# Connected Christmas village trial

The landscape had too many empty days; the sampler lost scene coherence. This trial uses one continuous snowy market scene for each marker palette, distributing houses, stalls, a decorated tree, windows, lanterns and parcels across the image. No separate icon panels are used, and scene objects cross the 9×9 daily boundaries.

Generated using the built-in image tool. Exact prompts and original images are saved in `inputs/clickart-village-prompt.txt`, `inputs/frixion-village-prompt.txt`, and the corresponding `*-village.png` files. Each run preserves source bytes and available generation metadata. Model, seed and generation cost were not exposed.

Both final mosaics use nearest-neighbour reduction followed by the existing fixed-palette mapping, with no manual pixel edits or dithering. An exploratory BOX comparison was inspected but introduced muddier boundaries, so the final runs use nearest. The exact 45×45 PNGs, 900×900 previews, 25 tiles, inventories, JSON maps and self-contained printable guides are in `clickart-village` and `frixion-village`.

| Palette | Fewest distinct colours in a day | Fewest colours occupying 3+ cells | Largest single-colour share in a day |
| --- | --- | --- | --- |
| clickart | 8 | 6 | 61.7% |
| frixion | 7 | 5 | 51.8% |

Both runs pass all artifact validation checks, including exact palette membership and deterministic reconversion. Every tile has substantial colour variety, but that is not proof of recognisability. The assistant's visual inspection finds a connected street, peaked rooftops, market stalls and decorated evergreen. Small people, faces, garlands and other fine details are partly lost or abstract. The source generator still drew more detail than the requested 45×45 simplicity.

Human judgement of the balance between overall scene readability and daily interest remains pending. No physical assembly trial has been performed. Earlier attempts remain available.
