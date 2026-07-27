# Content Agent V2 Integration — n8n Contract

## Status
Draft integration for PTR-AI DEV Server only. Do not publish automatically.

## Source of truth
- `docs/standards/content/PTR-CONTENT-STD-v2.0.md`
- `docs/standards/content/CONTENT-OUTPUT-CONTRACT-v1.0.md`
- PR #54 is a code and prompt reference only.

## Canonical output
Return a JSON-compatible object with these fields:

```yaml
request_id: string
mode: jewelry_expert | founder_presenter | ai_partner | asset_reuse
platform: []
objective: string
audience: string
language: th | en | bilingual
status: needs_review | needs_expert_review
core_message: string
hook: string
script: string
caption: {}
cta: string
keywords: []
hashtags: {}
scene_plan: []
asset_requirements: []
image_prompt: string
thumbnail_prompt: string
video_prompt: string
production_notes: []
accuracy_notes: []
risks: []
human_approval_required: true
approval_reason: []
```

## Compatibility mapping from PR #54

| PR #54 field | Canonical field |
|---|---|
| `content_analysis` | `objective`, `audience`, `core_message` |
| `spoken_script_th` | `script` |
| `timeline` | `scene_plan` |
| `veo_prompt` | `video_prompt` |
| `platform_captions` | `caption` |
| `platform_hashtags` | `hashtags` |
| `production_guide` | `production_notes` |
| `quality_review` | `accuracy_notes`, `risks` |
| `approval_status` | `status` |

## Permanent rules
- Spoken dialogue is Thai only.
- Veo scenes are 8 seconds when Veo output is requested.
- Default video specification is 1080p, 24fps.
- No on-screen text, subtitles, logo, or watermark.
- Do not invent measurements, tolerances, gem weights, prices, credentials, or customer facts.
- Face, voice, customer assets, and private media require explicit approval.
- `human_approval_required` must remain `true`.
- `status` must remain `needs_review` or `needs_expert_review`.
- Never claim content was published.

## Asset reuse placeholders
The request may include:

```yaml
asset_ids: []
asset_search_query: string
founder_visible: yes | no | optional
audio_permission: granted | denied | unknown
usage_rights: granted | restricted | unknown
```

Unknown permission or rights must create a risk and approval reason. The agent must not invent Asset IDs.

## PTR-AI DEV test

1. Deploy this branch to the DEV bot only.
2. Update the Content Agent node to follow the canonical output.
3. Keep the existing production workflow unchanged.
4. Run:

```text
!content คลิปสอน 45 วินาที เรื่อง AI ช่วยช่างทอง สำหรับ TikTok
```

5. Run asset reuse test:

```text
!content นำคลิปเก่าขับรถไปต่างจังหวัดมาทำวิดีโอเล่าเรื่อง 45 วินาที
```

6. Confirm:
- Discord receives a response within 2,000 characters or a safe summary.
- Canonical fields are present in the n8n execution data.
- No automatic publish node runs.
- Human approval remains required.
- Missing permissions are reported as risks.

## Merge gate
Do not mark this PR ready or merge until the DEV execution output is reviewed by the founder.
