# ai-video-production

AI 视频**生产执行手册**：分镜怎么拆（每 10 秒 4–6 镜）、角色/服装/道具/武器怎么锁、RGB 硬约束、白膜预演怎么走、复刻怎么从拆解派生、关键帧与成片怎么逐帧验收。

**适用场景**：真动手生产一段 AI 视频时——原创短片、广告、动作戏、参考视频复刻，在对话里生成或在画布工作流里执行，都按本手册动手与验收。

**与 video-production-workflow 的分工（防混）**：那个管**流程规矩**（museai-video 仓库、分镜表先行、每 10 秒一个任务、没配服务商只许称关键帧预览）；本 skill 管**动手执行**（镜头、锁、闸门的具体做法）。做视频时两个都读：先 workflow 定规矩，再按本手册执行。

---

# AI Video Production Workflow

## Build from a shot list, not a moving still

- Treat the shot as the smallest unit of a video, never the whole clip.

- Build every 10 second clip as 4 to 6 shots and give each shot its own duration, shot size, camera movement, subject action and transition.

- Check that the shot durations add up to the clip length and that shot sizes and camera movements vary across the clip.

- Build the 10 second product ad as a real ad with several shots, such as a product wide shot, a hand close up, a person medium shot and a product close up, instead of one shot that only moves.

- Ship three complete tutorial canvases when the user asks how to learn the workflow, with a simple 10 second single clip, an intermediate 30 second piece split into three clips and an advanced 60 second or longer multi character piece.

## Keep image to video and text to video apart

- Treat a keyframe in image to video as the first frame only and add a separate action prompt that describes what the subject does in the shot.

- Keep camera movement and subject movement as two separate fields, so a person turning, walking or picking up a product is not confused with a push, pull, pan, track or orbit.

- Cut the preview between a different keyframe for each shot and play each shot with its own movement and action, instead of stretching one image across the whole clip.

- Treat a reference image in text to video as the lock on character appearance and use the text prompt to describe the shot, instead of treating the reference image as the source of motion.

## Lock character and style consistency

- Give every character two entries, upload a reference image or generate one from an appearance description, and turn a generated character into reference assets with a front, side and back view.

- Bind each character to its reference images, its fixed appearance description and its fixed voice, and let each shot name the characters who appear in it.

- Offer all six reference image types as direct text to image generation, with character portrait, character three view, storyboard image, scene reference, product image, and costume or prop image.

- Default a new reference node to AI direct generation, and treat the appearance description as a generation input when no main description is present.

- Keep upload as an entry alongside generation, and keep the generate button enabled when either description field has text.

- Give a detachable key prop its own reference node in parallel with the character node, and connect both nodes to every storyboard, keyframe and video node that shows the prop.

- Keep only a short attribution line in the character node, such as where the prop hangs and when it is visible. Put the prop design spec and reference image in the prop node.

- Lock the project style in one style bible with art style, colour palette, lighting, framing, seed, negative prompt, voice and music style, and inject those values into every shot.

- Run the per-segment consistency check below before export, and block compositing while any segment is unchecked or failed.

## Previsualize action with a white model before you shoot it

- Run a white model pass before you shoot any action heavy segment, and place it between the storyboard and the video segment so motion is locked before appearance is swapped in.

- When replicating a reference video, white model poses are TRACED from the deconstruction's keyframes (pose transfer from the real frames), never invented from a text choreography. A white model sheet generated from text alone is invalid and must not be used: in the 2026-11-18 sword reset the white sheets were imagined from a wrong text breakdown, so every downstream pose was wrong from the source.

- Use a matte white ball joint mannequin as the base, with the male front neutral stance and the female front three quarter stance, and let the user switch the base or upload a custom one.

- Lock only duration and character swap and motion rhythm and camera and environment light in the white model pass, and keep character appearance and costume and props and colour under their own locks.

- Carry the RGB hard constraints and the costume fit lock and the body structure law from the earlier sections into the white model pass, and do not let the white model pass loosen any of them.

- Add a prop lock to the white model pass that records appearance and conservation and the position of the prop in each shot, and film each handover as its own shot.

- Remember the mannequin uses about seven head real proportions, so write the proportion guard into every prompt for a chibi character and state that the white model supplies only action and position while proportions follow the character card.

- Compare the white model frames with the finished frames at the same timestamps, and fail the segment when the action or position does not line up.

- Check the finished film for ball joint seams, and fail any shot where a seam is still visible.

- Say plainly when the pass is pose keyframe mode only, and name the missing video reference interface when true motion migration is not available.

- State in the delivery message where the white model node and template landed in the space, and name what was not tested yet.

## Enforce per-segment RGB consistency

- Read the pixel sampled colour table in `~/workspace/frames_check/COLOR_LOCK.md` and use its values as the lock values for each character, costume variant and key prop, instead of describing colours with adjectives.

- Write the lit, midtone and shadow HEX values plus the banned colours into each lock card, and put the corrected values into the affected shots when a check finds drift, instead of leaving them only in the global style bible.

- Sample colour from the midtone region of the character in each checked frame, away from highlights, shadows and background, and judge hue and saturation only, because brightness follows the scene light.

- Pass a colour only when its hue stays within 12 degrees and its saturation stays within 15 points of the lock value, and fail the segment when a colour crosses families, such as grey blue fur turning brown, or when saturation roughly doubles, such as pale orange fur turning saturated orange.

- Lock each costume variant on its own card with its category, cut, sleeve length, leg length, hood and pockets, plus its RGB values and banned styles, and never reuse one variant card for another outfit. In the rain night sword piece the pink hooded sweatshirt and beige trousers are one variant and the everyday pink satin collar is another.

- Check signature accessories in every segment and judge them by viewing angle. A front frame must show the bow and bell at the front of the throat, a side frame may show only their front edge, and a back frame may show only the pink band, so a bow on the back of the neck is a failure too.

- Block compositing while any segment is unchecked or failed, and check every 10 second segment on its own with at least 6 frames plus one frame inside every close up shot.

- When a segment fails, rewrite its shot prompts from the measured deviation instead of re-rolling it unchanged. Move a lost prop reference earlier in the image order, repeat the conservation and appearance locks in each affected shot, and add the proportion lock and the exact lighting wording when the style drifted toward realism.

- Run one final frame check across the finished stitched film, because splice points and cross segment drift only show at full length.

## Split long pieces and synthesize them

- Split any piece longer than 10 seconds into 10 second segments and give each segment its own shot list.

- Keep a synthesis step with a splice plan that lists each segment start and end time and the total duration, and show the total on the timeline.

- Offer 10 second, 30 second, 1 minute and longer targets and let the system split the script into numbered segments automatically.

## Replicate a reference video before you rebuild it

- STANDING RULE (V哥, 2026-11-18, "不需要我每次重复"): ALL video decomposition goes through rea-video (skill installed at ~/workspace/custom-skills/rea-video, CLI at ~/workspace/tools/rea-video/.venv/bin/rea-video), for every reference video and every task type — not only replicas, and without waiting for the user to name it. Follow the rea-video skill's full flow (survey → decompose → own visual review of low-confidence shots → apply-review) and use its outputs as the breakdown. Never substitute memory, the user's oral description, or ad-hoc frame extraction for a rea-video decomposition; the 2026-11-18 sword failure came from exactly that (invented breakdown → wrong storyboard, unverified keyframes, white-model poses imagined from text instead of traced from decomposed frames).

- Run the reverse engineering tool the user names before you break down a reference video, and do not substitute your own frame extraction for it.

- When the user hints at a reverse engineering skill or tool, find it, read its repository, install it, and run its full deconstruction on the reference video before you shoot anything. For the sword replica the tool was rea-video at github.com/JuneYaooo/rea-video, and its shot cuts, per shot reverse prompts and replica plan became the breakdown.

- Treat the tool output and the user's dictated choreography as the authoritative structure, and rebuild the shot list from them instead of from your first improvised breakdown.

- SINGLE SOURCE OF TRUTH (V哥, 2026-11-18, after the sword reset failed on mismatched layers): the deconstruction's keyframe set — per shot the first, middle and last frames plus every turning point, each with its timecode — is the ONLY source of truth for a replica. Storyboard cells, white model frames and character-swapped keyframes all derive from that same set and share its shot-frame IDs (shot N, frame M), so the layers cannot disagree by construction; any residual mismatch is one failed cell, regenerated alone.

- A storyboard for a replica is the deconstruction frame set PLUS annotations (time range and shot notes taken from the deconstruction). Never generate storyboard cell images from script or description text: a storyboard generated from text drifts from the real frames, and the text in the sword case was itself wrong. Where script text and a frame disagree, the frame wins and the text is corrected, never the other way round.

- LOCKS ARE CHECK ITEMS, NOT PROMPT DECORATION: a lock that exists only as prompt text does not exist. The costume lock includes STATE taken from the deconstruction (hood up versus hood down, hair worn out versus tied), not only garment type and colour — the original sword girl wears her hood DOWN with long hair out, and unchecked keyframes kept putting the hood on her head. The weapon lock carries a form spec, an exact count, banned forms (no scabbard when the source shows none), and a per-shot STATE LEDGER from the deconstruction (in hand, thrown, kicked away, back in hand), checked in every keyframe and every segment frame. The bell and signature-accessory locks are checked the same way: count, design and position, per keyframe, not only per finished segment.

- Generate one keyframe per storyboard cell before you shoot, and never use a still from the finished film as a keyframe.

- Keep every beat from the breakdown in the shot prompts, and restore a dropped beat instead of editing the breakdown to match a flawed take. In the sword replica the rotation, the kick and the slow motion were dropped from the prompts and had to be restored.

- Treat a user correction to the mechanics as a rewrite of the shot list, and check the corrected mechanics frame by frame before you call the take done. In the sword replica the correction was that the blade spins vertically like a windmill in front of the cat, the cat turns counter clockwise on her own, then she jumps and kicks the pommel with the tip horizontal and outward.

- Synthesize the exact contact instant as a still keyframe first when direct shooting cannot land a contact moment after repeated takes, verify the geometry in that keyframe, and then animate from it as the first frame. In the sword replica four direct takes failed, and the keyframe first route landed the pommel contact with the foot sole pressed on the pommel end cap, then the handle, the guard, the blade and the tip outward.

- Carry the replacement character's standing locks into every replica prompt, including gender presentation, hair length and footwear. For 咪咪 that means a female presentation, short fur with no long hair, and bare feet with no shoes, because one take invented a long ponytail and pink sneakers when those locks were missing.

- State before delivery that a replica is a re-enactment and not frame exact motion capture, because the video model has no motion capture, so beats and composition can match while limb trajectories cannot match frame by frame.

## Generate reference images in save-first stages

- Generate the image first and save it to the node at once, then add the appearance lock as a separate step.

- Keep each generation request to one heavy call, and keep the lock text short enough to fit in one call. In the video workflow space, trimming the lock text from about 7000 words to about 1100 words brought the lock step inside the gateway wait.

- Keep the saved image when the lock step fails, and re-run only the lock step instead of regenerating the image.

- Build a storyboard in two stages, first the table and then the images, so an interrupted run can resume from the saved table.

- Retry a failed generation call once, and show a plain language error that names the failed step.

## Mandatory pre-delivery verification gate (V哥 called out the same drift failure twice — 2026-11-10 对话篇 and 2026-11-11 铃铛大冒险； this gate exists so it cannot happen a third time)

- Anchors reduce drift but do NOT prove consistency. Only frame-by-frame checking does. Never deliver a stitched film on the strength of 1–2 sampled frames per segment.
- KEYFRAME GATE (added 2026-11-18, the gate whose absence sank the sword reset): the verification gate applies to KEYFRAMES before any video is generated, not only to finished segments. Every generated keyframe — storyboard cell image, white model frame, character-swapped keyframe — is READ side by side against its source deconstruction frame (pose and composition must match) and against the lock cards (costume state, accessory count/design/position, weapon form/count/state). An unchecked keyframe blocks video generation exactly as an unchecked segment blocks compositing. In the sword reset the segment gate compared takes against keyframes that were themselves wrong (a scabbard bar inherited from an unchecked sheet, the hood appearing and disappearing), so the gate passed garbage faithfully.
- For EVERY segment, extract at least 6 frames (roughly every 1.5s) PLUS one frame inside every close-up shot, and READ each frame against each character's lock card: head shape and muzzle length (chibi round/short vs mature long), age look, accessories present, limb count and bipedal stance, no duplicate characters, key-prop continuity (e.g. the bell is present/absent exactly where the plot says).
- Log the check in `~/workspace/frames_check/<project>/CHECK.md`: one line per frame (timestamp, verdict, what was checked). A segment counts as verified only when every sampled frame passes.
- REGENERATION VOIDS ALL PRIOR CHECKS for that segment. A re-rolled segment is a brand-new film: re-extract and re-read the full grid, including shots that were fine in the previous version. (This is exactly the step that was skipped for adventure part 2 v2 — only the totem frames were re-checked after the re-roll, and the regenerated deer gag had gone realistic.)
- A good LAST frame proves nothing about the middle of a shot. Sample inside shots, not just at boundaries. (Adventure part 3 v2's finale last frame was chibi while mid-finale frames had already drifted.)
- Use a VERIFIED frame from the previous segment as the next segment's visual anchor, and prefer an anchor from the same scene type (indoor anchor for indoor, garden for garden).
- In the delivery message, state the check coverage honestly (how many frames per segment were read, any frame that failed and what was done). Do not write "逐帧验过" unless the grid above was actually read.
- READ EVERY FRAME YOU EXTRACT. Adventure part 2 v3 passed with 6 frames extracted but only 4 read — the two unread frames hid exactly the defects V哥 then caught (mature profile deer; a head-only flower-bed close-up that read as a severed head). Extracting is not checking.
- Known model failure modes to check and design around: (a) side-profile chases age the deer up (long muzzle) — prefer front three-quarter angles for runs; (b) profile full-speed chases flip deer/cat to quadruped galloping — state a locomotion law (upright on two legs like children, arms pumping) AND use front angles; (c) extreme close-ups that crop to a lone head read as detached heads — falls and gags stay full-body medium shots, head always on visible shoulders; (d) every re-roll trades defects (one take fixed locomotion but lost the antlers and turned the owl brown) — check identity markers (antlers present, owl blue-grey not brown, bell count) on EVERY take, and when different takes each get different shots right, splice at shot level from verified takes instead of re-rolling forever.
- ANATOMY needs a written BODY-PLAN LAW, not just a limb count （V哥 caught six-limb readings twice; the count "exactly four limbs" alone failed): state WHERE the limbs attach - torso always VERTICAL like a standing child, head on top, two arms at the shoulders, two legs ONLY at the bottom of the torso, the back never horizontal like an animal's, never legs under the chest or belly. The model's default for an animal character is a quadruped body; a horizontal body with dangling arms reads as six limbs in motion even when a still frame seems to show four. Audit limb counts frame-by-frame on the final stitched film, not only per take.
- GROUP FINALES: a wide line-up of 4+ characters invites duplication (one take produced two owls in every group frame; a resume-chained take scrambled identities entirely - deer wearing the cat's bell, two deer, two owls). What held: a TIGHT CLUSTER composition (friends huddled/laughing together) fed with a VERIFIED group frame as anchor. When a chained/resumed generation scrambles the cast, regenerate fresh with verified-frame anchors instead of chaining further.
- IDENTITY CHECKS ARE NOT LOGIC CHECKS （V哥 caught a broken story chain in a segment whose frames each passed identity/count checks, 2026-11-11): for any action chain (a prop is lost, dropped, caught, handed over), trace the prop CONTINUOUSLY at ≤0.5s spacing across the whole beat and write a position ledger (who holds it at each step, and the exact frame where it changes hands). A segment fails if the prop teleports between sampled frames, even when every sampled frame has the right count. Design the chain so each transfer is ON CAMERA in its own shot; a solo-character insert shot (one character + the prop) is the reliable way to film a catch/handover without duplication.
- KEY-PROPS also need an APPEARANCE LOCK, not just a count （V哥 caught the bell changing design across segments, 2026-11-11): a conservation law keeps the NUMBER right, but each segment's model still draws its own version of the prop — the bell was a small round ball-bell on the cat's neck in segment 1, a plain flared bell in segment 2, and a large engraved temple bell in segment 3. Give the hero prop a design spec (shape, size relative to the holder, surface, details) and feed a reference image of the canonical prop in every segment that shows it, then check the design — not just the count — in every checked frame.
- FIXES ARE SEGMENT-SCOPED （V哥's standing instruction, 2026-11-11): never regenerate a whole multi-segment film for a local problem. Re-roll only the flagged segment (or the flagged shots inside it), keep the verified segments as the same files, and re-stitch. In the delivery message, state plainly which segments changed and which are untouched.
- KEY-PROPS need a written CONSERVATION LAW in the prompt (the mug fix in 对话篇， the bell fix in 铃铛大冒险）: state exactly how many exist, where each is at the start, and that it may only change location by being physically taken/dropped/caught — then COUNT the prop in every checked frame (a frame with the wrong count fails the segment). Watch for shape-morphing neighbours too: 月鹿's gold crescent pendant has been drawn bell-shaped for a few frames — check gold objects near the chest in close-ups.
- VOICE CAST is part of the lock card: state each character's voice (age + gender + timbre) in every prompt that has speech or vocalisation. 咪咪 is a soft cute FEMALE kitten — her voice must be written as a little-girl voice, never male （V哥 caught a male voice on her, 2026-11-11). The assistant cannot hear audio, so voice correctness can only be prompt-directed and must be flagged for the user's ear-check at delivery.
- CHASE DIRECTION must be composed, not assumed: a front charge toward camera reads as the prey being behind the chasers. For a pursuit, use a horizontal side-tracking shot and state the order in frame (prey at the front in the direction of travel, chasers behind it) — V哥's correction, 2026-11-11.
- LOCOMOTION CASTING LAW （V哥， 2026-11-11): each species travels its own way — birds (crow, owl) FLY during escapes and chases, ground characters run. Write it explicitly per character ("the crow is airborne the whole shot, feet tucked, never touches the ground; the owl flies behind it; the deer and the cat run on the path"). The model's default put a fleeing crow RUNNING on its feet and the owl walking. A ground-level GROUP anchor image anchors everyone to the ground — for flight chases use individual character references instead, and front three-quarter tracking kept the runners bipedal where a pure profile shot flipped the deer quadruped.
- A SNATCH/STEAL has the same logic structure as a catch: the thief must be shown EMPTY-handed on approach (claws visibly open and holding nothing) and the transfer must happen at the victim's body on camera. The model loves to spawn the thief already holding the loot the moment it enters frame; a dedicated two-character insert (victim + thief only) staged as dive → grab-at-the-neck → fly-off is the reliable build, and sub-ranges with the thief pre-holding the prop get trimmed out.

## State the output limits honestly

- Say once that a canvas preview shows keyframes plus movement parameters and is not a real mp4 file.

- Name the missing piece when real video is needed, such as an external video model interface the user must provide, and do not present keyframe animation as finished video.

## Available connectors

- [Runway](/opt/hatch/connectors/runway_mcp/CONNECTOR.md) for real video, image and audio generation when the user has connected it.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Ask which clip length and how many characters the piece needs before building, because those two answers decide the segment split and the character setup.

- Start from the closest tutorial canvas and change its shots, instead of building a long piece from an empty canvas.

- Verify the finished canvas by counting shots, shot sizes and subject actions in the 10 second ad before handing it over.

---

## 验收（本 skill 的执行验收）

- 分镜表在生成前已存在，每格有关键帧且关键帧已过关键帧闸门；每段 ≤10 秒且已逐段抽帧验过；失败只重生该段/该格；交付说明写明改了哪段、验了多少帧。
- 复刻类：拆解包在手（rea-video），分镜/白膜/关键帧与拆解帧共用编号且能逐格对应。

## 来源

2026-11-10 至 11-18 的真实生产沉淀（《铃铛大冒险》、对话篇/打斗篇、电商篇、《雨夜刀光》复刻、白膜太极案例）；2026-11-18 晚按 V哥指示正式入仓：同日《雨夜刀光》重置失败后补入拆解唯一真源、关键帧闸门、锁作检查项（服装状态锁/武器状态账）三条。本地执行副本在 ~/workspace/custom-skills/ai_video_production/，两处内容保持一致。
