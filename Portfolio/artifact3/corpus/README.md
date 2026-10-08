# Kestrel Home synthetic corpus

18 synthetic policy sources for Artifact #3. Fictional company, no real data.

## File format

Each file has YAML frontmatter with source-level metadata:

```yaml
source_id: S01
source_name: Returns FAQ
source_type: google_doc        # announcement | confluence | google_doc
channel: null                  # slack | legal_email, announcements only
authority_tier: 3              # 1 announcement, 2 confluence, 3 google_doc
owner: finance                 # finance | operations | legal | support
policy_area: returns           # returns | shipping | identity | warranty | payments | escalation | fraud
effective_date: null           # date the policy took effect, where stated
last_modified: 2025-08-14      # display only, never used for authority
expires_on: null               # announcements only
```

Each section begins with an access marker on its own line:

```text
<!-- access: agent -->
<!-- access: lead -->
```

The chunker splits on these markers first, then by size, so no chunk contains both access levels.

## Ground truth

Facts in these files match `corpus_plan.md`. Change the plan first, then the file.
