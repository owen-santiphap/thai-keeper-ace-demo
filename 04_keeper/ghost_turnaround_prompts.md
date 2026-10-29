# Ghost turnaround sheets (Gemini image -> image-to-3D)

Descriptions follow the keeper's lore (04_keeper/keeper_prompt_G_th.txt). One ghost per image.

## Shared sheet block (already included in each prompt below)

Character turnaround sheet for a 3D game asset: the same character shown 4 times side by side in one row,
left to right: FRONT view, LEFT SIDE view (profile), BACK view, 3/4 FRONT view. Identical design, scale,
colors and proportions in every view. Full body visible head to toe in every view, nothing cropped.
Neutral A-pose (arms 30 degrees from the body, palms facing in, fingers relaxed), feet flat, standing straight.
Orthographic camera at chest height, no perspective distortion. Even soft studio lighting, no cast shadows,
no rim light, no fog. Plain flat light-grey background (#D9D9D9). Stylized-realistic game character for
Unreal Engine, clean readable silhouette, PBR-friendly materials, clear separation between body, hair and clothes.
No text, no labels, no watermark, no frame, no props unless described, no ground plane.

## 1. กระสือ Krasue

Character turnaround sheet for a 3D game asset: the same character shown 4 times side by side in one row, left to right: FRONT, LEFT SIDE profile, BACK, 3/4 FRONT view. Identical design, scale and colors in every view, nothing cropped. Orthographic camera, even soft studio lighting, no shadows, plain flat light-grey background, no text or labels.
Subject: Krasue, a Thai folklore ghost: the floating head of a young Thai village woman with long straight black hair falling to the shoulders, pale skin, calm eerie face, slightly parted lips. Below the neck there is no body: a short stylized cluster of glowing internal organs hangs down (heart, lungs and a loose tangle of intestines), rendered stylized and non-gory like a glowing lantern, emitting a soft green-white glow. The head floats upright at adult head height, organs hanging straight down about one head length. Stylized-realistic game asset for Unreal Engine, clean silhouette, PBR-friendly materials, suitable for a school Halloween game (not gory, no blood).

## 2. นางตานี Nang Tani

Character turnaround sheet for a 3D game asset: the same character shown 4 times side by side in one row, left to right: FRONT, LEFT SIDE profile, BACK, 3/4 FRONT view. Identical design, scale and colors in every view, full body head to toe, nothing cropped. Neutral A-pose, feet flat. Orthographic camera, even soft studio lighting, no shadows, plain flat light-grey background, no text or labels.
Subject: Nang Tani, a beautiful Thai female tree spirit who lives in a wild banana (kluay tani) grove. Young woman, gentle face, long black hair loosely tied with a few strands falling, bare feet. Traditional Thai dress in banana-leaf green: a fitted pha sin skirt to the ankles with a subtle woven pattern and a sabai shoulder cloth draped over one shoulder, slightly translucent fabric edges that hint she is a spirit. A few colored ribbons (pink, saffron) tied around her wrist like the ribbons villagers tie on banana trees. Pale moonlit skin with a very faint glow. Stylized-realistic game asset for Unreal Engine, clean silhouette, PBR-friendly materials, kind but uncanny, suitable for a school Halloween game.

## 3. ผีกองกอย Phi Kong Koi

Character turnaround sheet for a 3D game asset: the same character shown 4 times side by side in one row, left to right: FRONT, LEFT SIDE profile, BACK, 3/4 FRONT view. Identical design, scale and colors in every view, full body, nothing cropped. Standing still balanced on its single leg, arms slightly away from the body. Orthographic camera, even soft studio lighting, no shadows, plain flat light-grey background, no text or labels.
Subject: Phi Kong Koi, a Thai deep-forest ghost that has only ONE leg (a single strong leg in the center of the body, large bare foot with long toes) and moves by hopping. Small wiry humanoid about 140 cm tall, hunched posture, long thin arms with long fingers, dark mossy-brown skin with bark-like texture, tangled long black hair with a few leaves and twigs caught in it, large round night-animal eyes, small mouth. Wears only a torn earth-colored loincloth. Stylized-realistic game asset for Unreal Engine, clean silhouette, PBR-friendly materials, creepy but not gory, suitable for a school Halloween game.

## 4. เปรต Pret (Preta)

Character turnaround sheet for a 3D game asset: the same character shown 4 times side by side in one row, left to right: FRONT, LEFT SIDE profile, BACK, 3/4 FRONT view. Identical design, scale and colors in every view, full body head to toe, nothing cropped. Neutral A-pose, feet flat. Orthographic camera, even soft studio lighting, no shadows, plain flat light-grey background, no text or labels.
Subject: Pret, a Thai Buddhist hungry ghost as painted on Thai temple murals. Extremely tall and emaciated humanoid (proportions as tall as a sugar palm tree: very long legs and torso, very long thin neck), ribs and joints visible, sunken belly, pale ash-grey skin. Enormous hands as big as palm-leaf fans hanging from thin arms. A tiny mouth no bigger than a needle hole, hollow sad eyes, sparse long white hair. Wears a ragged grey cloth around the waist. Sorrowful rather than aggressive. Stylized-realistic game asset for Unreal Engine with a hint of Thai mural line style, clean silhouette, PBR-friendly materials, suitable for a school Halloween game (not gory).

## If the 3D tool wants one front image instead of a sheet

Use the same prompt but replace the first sentence with:
"Single full-body FRONT view of one character for image-to-3D, centered, whole body in frame with margin, ..."
Then feed the front image (and the side/back views if the tool accepts multi-view) to the 3D generator.

## Tips

- Generate, then ask Gemini: "Same character, keep everything identical, fix: <problem>" instead of re-rolling.
- Check that all 4 views match (hair, clothes, colors) before converting; mismatched views give broken meshes.
- For the game, Pret will be scaled up in Unreal (he is meant to look as tall as a sugar palm); keep the sheet at normal proportions.
- After import: one material per mesh, keep textures at 1K-2K (the laptop is near its 8 GB VRAM limit with the MetaHuman keeper).
