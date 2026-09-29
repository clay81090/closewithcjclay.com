---
name: htsa-close-page
description: >-
  Builds HTSA close/enrollment pages from templates/_TEMPLATE-close.html or clones.
  Enrollment-only (no precall resources). Post-pay: one welcome email, 3 green
  next-steps. Use htsa-paste-close.py --ship on call.
---

# HTSA close page (agent skill)

**Authoritative rules:** `.cursor/rules/htsa-close-page.mdc` and `.cursor/rules/htsa-page-map.mdc`

## Post-payment onboarding (Sept 2026+)

Members receive **one welcome email** from HTSA after payment. **Never** copy that says two emails, a second login email, or waiting for credentials.

**After you pay** dropdown (green outline). Summary: **Self enroll or a 5 minute call
with CJ — pick your path.** Inside, two tabs:

**Path A — Self Enroll** (3 steps):

1. **Welcome email + Sales Training Login** — Star/bookmark the welcome email. Click **Sales Training Login Link (Bookmark this)**, use their email to create a password, start course modules. Come back to the email later for Zoom links.
   - Login URL: `https://members.highticketsalesacademy.com/users/sign_in`
2. **Book kickoff with Mark** — `https://meetings.hubspot.com/chad-aleo/member-success-team-kickoff-call`
3. **Join Mastermind** — `https://www.facebook.com/groups/1039656943556821`

**Path B — 5 Minute Call with CJ** — Call or text CJ at `(616) 612-1735`. CJ walks them through welcome email, login, Mark kickoff, and Mastermind live. SMS body: `Payment made - ready for next steps`

Template constant (do not remove):

```js
const ONBOARDING = {
  trainingLogin: "https://members.highticketsalesacademy.com/users/sign_in",
  kickoffUrl:    "https://meetings.hubspot.com/chad-aleo/member-success-team-kickoff-call",
  mastermindUrl: "https://www.facebook.com/groups/1039656943556821",
  cjPhone:       "+16166121735",
  cjSmsBody:     "Payment made - ready for next steps"
};
```

## Enrollment-only layout

Close pages **do not** include:

- All HTSA Resources tab
- Proof squares / videos / Trustpilot blocks
- CJ Reviews

Put proof and resources on **pre-call** pages (`r/<first>_<last>/index.html`).

## On-call ship

```bash
python3 scripts/htsa-paste-close.py --ship <<'EOF'
same as: 4
Full Name
Email: test@example.com
Phone Number: +1 (555) 555-0100
EOF
```

Wait for `READY`. Print EMAIL + TEXT from `scripts/htsa_close_copy.py` voice (no proof section).
