# Test plan: EU AI Act Risk Check

Rulebook v2026.10. Generated from `tests/acceptance_cases.yaml` by `scripts/make_test_plan.py`.
The same cases run automatically on every push (`tests/test_acceptance.py`).

## How to run a case

1. Reload the app so every box is unticked.
2. Set **Your role** as listed.
3. Open the section named before each question and tick only the boxes listed.
4. Compare the result panel with **Expected**. Tick the case off if everything matches.

## Before you start: app checks

- [ ] The app loads without errors and shows **Minimal risk** with nothing ticked
- [ ] **Load an example** fills in the boxes (try *CV screening tool*: should show **High risk**)
- [ ] Switching **Your role** changes the list under *What you need to do*
- [ ] **Download report** gives a Markdown file with the result, citations, a checklist and the line *not legal advice*
- [ ] The *readable YAML file* link in the sidebar opens the rulebook on GitHub
- [ ] The app works on a phone (questions stack above the result)

## Scenarios

### TC01 Spam filter

*An email spam filter used internally by a company.*

**Role:** Deployer

**Tick:** nothing

**Expected:** Minimal risk
- To-do list includes: Art. 4 (as amended by Reg. (EU) 2026/1744)
- 1 item(s) under *What you need to do*

- [ ] Pass

### TC02 AI toy without third-party assessment

*A toy with a small AI feature. Toy rules apply, but no notified body is involved.*

**Role:** Provider

**Tick:**
- 3. Products and safety components: *The AI is itself a product, or a safety component of a product, covered by EU product legislation in Annex I*

**Expected:** Minimal risk
- To-do list does **not** include: Art. 9
- 1 item(s) under *What you need to do*

- [ ] Pass

### TC03 Customer service chatbot

*A company builds and launches a chatbot that answers customers in writing.*

**Role:** Provider

**Tick:**
- 6. Transparency: *Interacts directly with people (e.g. chatbot, voice assistant)*
- 6. Transparency: *Generates synthetic audio, images, video or text*

**Expected:** Transparency obligations
- Why shows: Art. 50(1), Art. 50(2)
- To-do list includes: Art. 50(1), Art. 50(2)
- 3 item(s) under *What you need to do*

- [ ] Pass

### TC04 Deepfake in a marketing video

*A brand uses an AI-generated video of a realistic person in an ad.*

**Role:** Deployer

**Tick:**
- 6. Transparency: *Generates or manipulates images, audio or video that could pass as real (deepfakes)*

**Expected:** Transparency obligations
- Why shows: Art. 50(4)
- To-do list includes: Art. 50(4)
- 2 item(s) under *What you need to do*

- [ ] Pass

### TC05 AI-written public interest news

*A local news site publishes AI-written articles on council decisions without an editor.*

**Role:** Deployer

**Tick:**
- 6. Transparency: *Publishes AI-generated text to inform the public on matters of public interest, without human editorial review*

**Expected:** Transparency obligations
- To-do list includes: Art. 50(4)
- 2 item(s) under *What you need to do*

- [ ] Pass

### TC06 CV screening at a private company

*HR uses a bought-in tool that ranks job applicants.*

**Role:** Deployer

**Tick:**
- 4. High-risk use areas: *Employment: recruiting, screening or evaluating candidates, or decisions on promotion, termination, task allocation or performance*

**Expected:** High risk
- Why shows: Art. 6(2), Annex III point 4
- Applies from 2 December 2027
- To-do list includes: Art. 26(2), Art. 26(6), Art. 26(7), Art. 86
- To-do list does **not** include: Art. 27, Art. 9
- 9 item(s) under *What you need to do*

- [ ] Pass

### TC07 Same CV tool, seen from the vendor

*The software company that builds and sells the CV screening tool.*

**Role:** Provider

**Tick:**
- 4. High-risk use areas: *Employment: recruiting, screening or evaluating candidates, or decisions on promotion, termination, task allocation or performance*

**Expected:** High risk
- To-do list includes: Art. 9, Art. 10, Art. 14, Art. 17, Art. 49
- To-do list does **not** include: Art. 26(1)
- 12 item(s) under *What you need to do*

- [ ] Pass

### TC08 Bank credit scoring

*A bank scores consumers' creditworthiness before granting loans.*

**Role:** Deployer

**Tick:**
- 4. High-risk use areas: *Credit: evaluating creditworthiness or setting credit scores of people (fraud detection excluded)*
- 5. Exceptions for high-risk use areas: *The system profiles natural persons (automated evaluation of personal aspects such as performance, reliability, behaviour)*

**Expected:** High risk
- Why shows: Art. 6(2), Annex III point 5(b)
- To-do list includes: Art. 27
- 10 item(s) under *What you need to do*

- [ ] Pass

### TC09 Life insurance pricing

*A pension and insurance company prices life insurance with an AI model.*

**Role:** Deployer

**Tick:**
- 4. High-risk use areas: *Insurance: risk assessment and pricing for people in life and health insurance*

**Expected:** High risk
- Why shows: Art. 6(2), Annex III point 5(c)
- To-do list includes: Art. 27
- 10 item(s) under *What you need to do*

- [ ] Pass

### TC10 Municipality benefits assessment

*A municipality uses AI to assess eligibility for social benefits.*

**Role:** Deployer

**Tick:**
- 4. High-risk use areas: *Public services: a public authority evaluating eligibility for public assistance benefits and services, including healthcare*
- 7. Context: *You are a public body, or a private organisation providing public services*

**Expected:** High risk
- Why shows: Art. 6(2), Annex III point 5(a)
- To-do list includes: Art. 27
- 10 item(s) under *What you need to do*

- [ ] Pass

### TC11 Exam proctoring

*A university uses AI to flag cheating during online exams.*

**Role:** Deployer

**Tick:**
- 4. High-risk use areas: *Education: admission, grading or evaluating learning outcomes, assessing education level, or monitoring cheating in tests*

**Expected:** High risk
- Why shows: Art. 6(2), Annex III point 3
- 9 item(s) under *What you need to do*

- [ ] Pass

### TC12 AI in a medical device

*Diagnostic software that is a medical device and needs a notified body.*

**Role:** Provider

**Tick:**
- 3. Products and safety components: *The AI is itself a product, or a safety component of a product, covered by EU product legislation in Annex I*
- 3. Products and safety components: *That product must undergo a third-party conformity assessment*

**Expected:** High risk
- Why shows: Art. 6(1), Annex I
- Applies from 2 August 2028
- 12 item(s) under *What you need to do*

- [ ] Pass

### TC13 HR document sorter

*A tool that only sorts incoming HR documents into folders. No decisions about people.*

**Role:** Provider

**Tick:**
- 4. High-risk use areas: *Employment: recruiting, screening or evaluating candidates, or decisions on promotion, termination, task allocation or performance*
- 5. Exceptions for high-risk use areas: *It only performs a narrow procedural task (e.g. sorting documents into categories)*

**Expected:** Minimal risk
- Why shows: Art. 6(3), Art. 6(4), Art. 49(2)
- To-do list includes: Art. 6(4), Art. 49(2)
- 3 item(s) under *What you need to do*

- [ ] Pass

### TC14 Preparatory HR tool that profiles people

*A tool that prepares candidate summaries, but builds a profile of each person.*

**Role:** Provider

**Tick:**
- 4. High-risk use areas: *Employment: recruiting, screening or evaluating candidates, or decisions on promotion, termination, task allocation or performance*
- 5. Exceptions for high-risk use areas: *It only performs a preparatory task for an assessment made by a human*
- 5. Exceptions for high-risk use areas: *The system profiles natural persons (automated evaluation of personal aspects such as performance, reliability, behaviour)*

**Expected:** High risk
- To-do list does **not** include: Art. 6(4)
- 12 item(s) under *What you need to do*

- [ ] Pass

### TC15 Emotion tracking of employees

*A call centre uses AI to read agents' emotions from their voice.*

**Role:** Deployer

**Tick:**
- 2. Prohibited practices: *Infers emotions of people in the workplace or in education (not for medical or safety reasons)*

**Expected:** Prohibited
- Why shows: Art. 5(1)(f)
- To-do list includes: Art. 5, Art. 99(3)
- 3 item(s) under *What you need to do*

- [ ] Pass

### TC16 Social scoring hidden in a chatbot

*A chatbot that also scores citizens on social behaviour.*

**Role:** Provider and deployer

**Tick:**
- 2. Prohibited practices: *Scores or classifies people based on social behaviour or personal traits, leading to unjustified or disproportionate detrimental treatment*
- 6. Transparency: *Interacts directly with people (e.g. chatbot, voice assistant)*

**Expected:** Prohibited
- Why shows: Art. 5(1)(c), Art. 50(1)
- 4 item(s) under *What you need to do*

- [ ] Pass

### TC17 Nudify app

*An app that creates explicit images of real people from normal photos.*

**Role:** Provider

**Tick:**
- 2. Prohibited practices: *Creates or manipulates realistic intimate or sexually explicit images of an identifiable person without their consent*
- 6. Transparency: *Generates synthetic audio, images, video or text*

**Expected:** Prohibited
- Why shows: Art. 5, as amended by Reg. (EU) 2026/1744
- Applies from 2 December 2026
- 4 item(s) under *What you need to do*

- [ ] Pass

### TC18 Military targeting system

*A defence system using facial recognition, used only for military purposes.*

**Role:** Provider

**Tick:**
- 1. Scope: *Used exclusively for military, defence or national security purposes*
- 4. High-risk use areas: *Biometrics: remote biometric identification, biometric categorisation by sensitive traits, or emotion recognition*

**Expected:** Out of scope
- Why shows: Art. 2(3)
- To-do list does **not** include: Art. 4 (as amended by Reg. (EU) 2026/1744)
- 0 item(s) under *What you need to do*

- [ ] Pass

### TC19 Lab prototype

*A research prototype that has not been launched or tested in real-world conditions.*

**Role:** Provider

**Tick:**
- 1. Scope: *Still in research, testing or development and not yet placed on the market or put into service*
- 4. High-risk use areas: *Credit: evaluating creditworthiness or setting credit scores of people (fraud detection excluded)*

**Expected:** Out of scope
- Why shows: Art. 2(8)
- 0 item(s) under *What you need to do*

- [ ] Pass

### TC20 Company releasing its own foundation model

*A startup trains and publishes its own general-purpose language model.*

**Role:** Provider

**Tick:**
- 7. Context: *You develop and release a general-purpose AI model yourself (not just use one through an API)*

**Expected:** Minimal risk
- Why shows: Arts. 53 and 55
- To-do list includes: Art. 53(1)(c), Art. 53(1)(d)
- 5 item(s) under *What you need to do*

- [ ] Pass

## If a case fails

Note the case id, what you ticked and what the app showed, and open an issue on GitHub.
If the law has changed, update the rulebook, bump its version, and update the expected result in `tests/acceptance_cases.yaml`.
