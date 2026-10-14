# RAG Evaluation Results

Methods compared: **vector** (cosine top-4) vs **rerank** (vector top-20, re-scored with a cross-encoder, keep top-4).

## Summary table

| Q | Question | Method | Retrieved Chunks | Retrieval Time (s) | Total Response Time (s) | Answer Quality |
|---|---|---|---|---|---|---|
| 1 | What file types must the app support for ingestion? | vector | 4 | 0.024 | 2.05 | 5 |
| 1 | What file types must the app support for ingestion? | rerank | 4 | 0.951 | 1.59 | 5 |
| 2 | What artifacts are required and what format are they saved i | vector | 4 | 0.02 | 0.62 | 5 |
| 2 | What artifacts are required and what format are they saved i | rerank | 4 | 0.644 | 1.54 | 5 |
| 3 | What should the deployment demonstration show? | vector | 4 | 0.025 | 8.87 | 3 |
| 3 | What should the deployment demonstration show? | rerank | 4 | 0.373 | 7.58 | 4 |
| 4 | Where must API tokens be stored for CI/CD? | vector | 4 | 0.022 | 5.73 | 5 |
| 4 | Where must API tokens be stored for CI/CD? | rerank | 4 | 0.353 | 8.98 | 5 |
| 5 | What should students do if the deployment has persistent sto | vector | 4 | 0.023 | 9.78 | 5 |
| 5 | What should students do if the deployment has persistent sto | rerank | 4 | 0.37 | 5.31 | 5 |
| 6 | What is the professor's favorite color? | vector | 4 | 0.026 | 7.48 | 4 |
| 6 | What is the professor's favorite color? | rerank | 4 | 0.361 | 7.07 | 5 |

## Averages

| Method | Avg Retrieval (s) | Avg Total (s) |
|---|---|---|
| vector | 0.023 | 5.75 |
| rerank | 0.509 | 5.34 |

## Chunk overlap between methods

How many of the top chunks both methods agreed on (low overlap = reranking changed what the LLM saw).

| Q | Shared chunks |
|---|---|
| 1 | 2 / 4 |
| 2 | 4 / 4 |
| 3 | 3 / 4 |
| 4 | 2 / 4 |
| 5 | 3 / 4 |
| 6 | 0 / 4 |

## Details per question

### Q1 [vector]: What file types must the app support for ingestion?

**Expected:** PDF, PPTX, TXT, and web URLs

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 1* (score 0.3542): techniques,   backend   services,   a   user   interface,   data   storage,   and   cloud   deployment   into   one   working   application.  1.   Required   Features   Your   application   must   sup...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 2* (score 0.3384): uploaded/linked   sources.   Your   application   should   also   store   the   conversation   so   that   users   can   return   to   a   notebook   and   view   previous   messages.  3.   Artifact  ...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 8* (score 0.3143): tools .   However,   you   should   first   establish   the   application   design/specification   before   generating   the   implementation.  12.   Advanced   Features   —   Optional   The   followi...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 5* (score 0.2984): with   the   application   ●   Include   all   required   dependencies   ●   Use   environment   variables/secrets   for   API   keys   ●   Not   contain   API   keys   or   other   secrets   in   the...

**Answer** (2.05s):

The application must let users ingest the following file types:

- PDF files  
- PPTX files  
- TXT files  
- Web URLs  

These requirements are listed in the “Source Ingestion” section of the notebook specifications【1】.

### Q1 [rerank]: What file types must the app support for ingestion?

**Expected:** PDF, PPTX, TXT, and web URLs

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 1* (score 3.3104): techniques,   backend   services,   a   user   interface,   data   storage,   and   cloud   deployment   into   one   working   application.  1.   Required   Features   Your   application   must   sup...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score -4.5127): 15.   Submission   Checklist  Use   the   following   checklist   to   verify   you   have   completed   all   the   requirements:  Application  Application   runs   locally  Application   runs   on  ...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 2* (score -9.1674): uploaded/linked   sources.   Your   application   should   also   store   the   conversation   so   that   users   can   return   to   a   notebook   and   view   previous   messages.  3.   Artifact  ...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 4* (score -9.2652): ●   Notebook   management   ●   Source   upload   ●   URL   ingestion   ●   Chat   ●   Citations   ●   Artifact   generation   ●   Artifact   viewing/downloading   ●   Error   messages   when   someth...

**Answer** (1.59s):

The application must be able to ingest the following file types:

- **PDF files**  
- **PPTX files**  
- **TXT files**  
- **Web URLs**  

These requirements are listed in the project specifications and the submission checklist[1][2].

### Q2 [vector]: What artifacts are required and what format are they saved in?

**Expected:** A report and a quiz with an answer key, saved as .md

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 8* (score 0.494): tools .   However,   you   should   first   establish   the   application   design/specification   before   generating   the   implementation.  12.   Advanced   Features   —   Optional   The   followi...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 2* (score 0.4894): uploaded/linked   sources.   Your   application   should   also   store   the   conversation   so   that   users   can   return   to   a   notebook   and   view   previous   messages.  3.   Artifact  ...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.3869): Quiz   ●   Generate   a   quiz   based   on   the   notebook   sources   ●   Save   the   quiz   as   a   .md   file   ●   Include   an   answer   key   ●   Allow   the   user   to   view   or   downl...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score 0.36): 15.   Submission   Checklist  Use   the   following   checklist   to   verify   you   have   completed   all   the   requirements:  Application  Application   runs   locally  Application   runs   on  ...

**Answer** (0.62s):

**Required artifacts**

| Artifact | Required by the project | File format it must be saved in |
|----------|------------------------|---------------------------------|
| Report   | Must be generated from the notebook sources | Saved as a **Markdown (.md)** file【2】 |
| Quiz     | Must be generated from the notebook sources (including an answer key) | Saved as a **Markdown (.md)** file【3】 |

These two artifacts (report and quiz) are the only ones explicitly required; other artifact types are listed as optional.

### Q2 [rerank]: What artifacts are required and what format are they saved in?

**Expected:** A report and a quiz with an answer key, saved as .md

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 2* (score 1.2201): uploaded/linked   sources.   Your   application   should   also   store   the   conversation   so   that   users   can   return   to   a   notebook   and   view   previous   messages.  3.   Artifact  ...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.2854): Quiz   ●   Generate   a   quiz   based   on   the   notebook   sources   ●   Save   the   quiz   as   a   .md   file   ●   Include   an   answer   key   ●   Allow   the   user   to   view   or   downl...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score -4.2786): 15.   Submission   Checklist  Use   the   following   checklist   to   verify   you   have   completed   all   the   requirements:  Application  Application   runs   locally  Application   runs   on  ...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 8* (score -4.3974): tools .   However,   you   should   first   establish   the   application   design/specification   before   generating   the   implementation.  12.   Advanced   Features   —   Optional   The   followi...

**Answer** (1.54s):

The required artifacts are:

| Artifact | Required by the specification | File format it must be saved as |
|----------|------------------------------|---------------------------------|
| **Report** | Must be generated from the notebook sources and made viewable/downloadable | Saved as a **`.md` (Markdown) file**【1】 |
| **Quiz** | Must be generated from the notebook sources, include an answer key, and be viewable/downloadable | Saved as a **`.md` (Markdown) file**【2】 |

These are the only artifacts that the project description lists as mandatory; other artifact types (e.g., podcast transcript, flashcards, mind maps) are mentioned as optional enhancements【2】【4】.

### Q3 [vector]: What should the deployment demonstration show?

**Expected:** Live platform, notebook, adding a source, RAG question, citation, artifact, GitHub Actions deploy

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 9* (score 0.5132): 13.   Deliverables   Submit:   1.   GitHub   Repository   Your   repository   should   contain:   ●   Source   code   ●   README   ●   Requirements/dependencies   ●   GitHub   Actions   workflow   ●  ...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 6* (score 0.4567): 8.   GitHub   Actions   /   CI/CD   Set   up   a   GitHub   Actions   workflow   that   automatically   deploys   changes   to   your   cloud   deployment   platform.   The   expected   workflow   is:...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 7* (score 0.4511): The   demonstration   may   be   a   short   screen   recording.  10.   Architecture   Documentation   Submit   a   short   architecture   document   containing:   Architecture   Diagram   Show   the ...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 11* (score 0.3909): Source   code   is   committed  .gitignore   is   included  GitHub   Actions   workflow   is   included  Pushes   trigger   deployment  Deployment   completes   successfully   Documentation  Architect...

**Answer** (8.87s):

The deployment demonstration should include a short 1–2 minute screen recording that shows:

1. Your live cloud‑deployment platform.  
2. Creating or selecting a notebook.  
3. Adding a source to the notebook.  
4. Asking a RAG question.  
5. Displaying the citation returned for the answer.  
6. Generating an artifact.  
7. The GitHub Actions workflow successfully deploying the application【2】.

### Q3 [rerank]: What should the deployment demonstration show?

**Expected:** Live platform, notebook, adding a source, RAG question, citation, artifact, GitHub Actions deploy

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 6* (score 6.59): 8.   GitHub   Actions   /   CI/CD   Set   up   a   GitHub   Actions   workflow   that   automatically   deploys   changes   to   your   cloud   deployment   platform.   The   expected   workflow   is:...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 7* (score 2.8812): The   demonstration   may   be   a   short   screen   recording.  10.   Architecture   Documentation   Submit   a   short   architecture   document   containing:   Architecture   Diagram   Show   the ...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 9* (score 1.9077): 13.   Deliverables   Submit:   1.   GitHub   Repository   Your   repository   should   contain:   ●   Source   code   ●   README   ●   Requirements/dependencies   ●   GitHub   Actions   workflow   ●  ...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score 1.4884): successfully  Required   dependencies   are   included  API   keys   are   stored   as   secrets  No   API   keys   are   committed   to   GitHub  README   explains   the   application  Storage   beha...

**Answer** (7.58s):

The deployment demonstration must illustrate the end‑to‑end workflow of the application. Specifically, it should show:

1. **Your live cloud deployment platform** – the running instance of the app.  
2. **Creating or selecting a notebook** within the app.  
3. **Adding a source** (e.g., a document or data file) to that notebook.  
4. **Asking a RAG (retrieval‑augmented generation) question** against the notebook.  
5. **Displaying a citation** for the retrieved information.  
6. **Generating an artifact** (e.g., a report, summary, or other output).  
7. **The GitHub Actions workflow** successfully executing and deploying the updated application.  

These points are listed in the project guidelines for the deployment demonstration【1】.

### Q4 [vector]: Where must API tokens be stored for CI/CD?

**Expected:** GitHub Secrets, not committed to the repo

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score 0.4017): successfully  Required   dependencies   are   included  API   keys   are   stored   as   secrets  No   API   keys   are   committed   to   GitHub  README   explains   the   application  Storage   beha...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 5* (score 0.3428): with   the   application   ●   Include   all   required   dependencies   ●   Use   environment   variables/secrets   for   API   keys   ●   Not   contain   API   keys   or   other   secrets   in   the...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 6* (score 0.2972): 8.   GitHub   Actions   /   CI/CD   Set   up   a   GitHub   Actions   workflow   that   automatically   deploys   changes   to   your   cloud   deployment   platform.   The   expected   workflow   is:...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.2422): the   deployment   environment   has   limitations   on   persistent   storage,   document   those   limitations   rather   than   trying   to   solve   them   with   unnecessary   infrastructure.  5....

**Answer** (5.73s):

API tokens (or other secrets) must be stored using **GitHub Secrets**, not committed directly to the repository [3].

### Q4 [rerank]: Where must API tokens be stored for CI/CD?

**Expected:** GitHub Secrets, not committed to the repo

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 6* (score 4.849): 8.   GitHub   Actions   /   CI/CD   Set   up   a   GitHub   Actions   workflow   that   automatically   deploys   changes   to   your   cloud   deployment   platform.   The   expected   workflow   is:...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score -4.6438): successfully  Required   dependencies   are   included  API   keys   are   stored   as   secrets  No   API   keys   are   committed   to   GitHub  README   explains   the   application  Storage   beha...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 9* (score -6.2251): 13.   Deliverables   Submit:   1.   GitHub   Repository   Your   repository   should   contain:   ●   Source   code   ●   README   ●   Requirements/dependencies   ●   GitHub   Actions   workflow   ●  ...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score -8.1612): 15.   Submission   Checklist  Use   the   following   checklist   to   verify   you   have   completed   all   the   requirements:  Application  Application   runs   locally  Application   runs   on  ...

**Answer** (8.98s):

API tokens (or other secrets) must be stored as **GitHub Secrets** rather than being committed to the repository — this is required for the CI/CD workflow. 【1】

### Q5 [vector]: What should students do if the deployment has persistent storage limits?

**Expected:** Document the limitations instead of adding unnecessary infrastructure

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.5607): the   deployment   environment   has   limitations   on   persistent   storage,   document   those   limitations   rather   than   trying   to   solve   them   with   unnecessary   infrastructure.  5....
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 1* (score 0.3553): techniques,   backend   services,   a   user   interface,   data   storage,   and   cloud   deployment   into   one   working   application.  1.   Required   Features   Your   application   must   sup...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.3526): Quiz   ●   Generate   a   quiz   based   on   the   notebook   sources   ●   Save   the   quiz   as   a   .md   file   ●   Include   an   answer   key   ●   Allow   the   user   to   view   or   downl...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score 0.3314): 15.   Submission   Checklist  Use   the   following   checklist   to   verify   you   have   completed   all   the   requirements:  Application  Application   runs   locally  Application   runs   on  ...

**Answer** (9.78s):

If the deployment environment imposes limits on persistent storage, students should **document those limitations** instead of attempting to work around them with extra infrastructure — the project guidelines explicitly ask for this documentation rather than a technical fix[1].

### Q5 [rerank]: What should students do if the deployment has persistent storage limits?

**Expected:** Document the limitations instead of adding unnecessary infrastructure

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 4.3558): the   deployment   environment   has   limitations   on   persistent   storage,   document   those   limitations   rather   than   trying   to   solve   them   with   unnecessary   infrastructure.  5....
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.4033): Quiz   ●   Generate   a   quiz   based   on   the   notebook   sources   ●   Save   the   quiz   as   a   .md   file   ●   Include   an   answer   key   ●   Allow   the   user   to   view   or   downl...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score -6.5834): successfully  Required   dependencies   are   included  API   keys   are   stored   as   secrets  No   API   keys   are   committed   to   GitHub  README   explains   the   application  Storage   beha...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 1* (score -9.2093): techniques,   backend   services,   a   user   interface,   data   storage,   and   cloud   deployment   into   one   working   application.  1.   Required   Features   Your   application   must   sup...

**Answer** (5.31s):

If the deployment environment imposes limits on persistent storage, students should **document those limitations** instead of attempting to work around them with additional infrastructure — the project guidelines explicitly require that the storage constraints be recorded rather than “solved” with unnecessary resources[1][2].

### Q6 [vector]: What is the professor's favorite color?

**Expected:** Not in the sources; should say it can't find it

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 4* (score 0.1177): were   retrieved   ●   How   the   techniques   affected   answer   quality   ●   Response   time   ●   Which   approach   you   selected   and   why   You   do   not   need   to   build   a   highly ...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score 0.1133): Quiz   ●   Generate   a   quiz   based   on   the   notebook   sources   ●   Save   the   quiz   as   a   .md   file   ●   Include   an   answer   key   ●   Allow   the   user   to   view   or   downl...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 4* (score 0.0785): ●   Notebook   management   ●   Source   upload   ●   URL   ingestion   ●   Chat   ●   Citations   ●   Artifact   generation   ●   Artifact   viewing/downloading   ●   Error   messages   when   someth...
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 10* (score 0.0652): 15.   Submission   Checklist  Use   the   following   checklist   to   verify   you   have   completed   all   the   requirements:  Application  Application   runs   locally  Application   runs   on  ...

**Answer** (7.48s):

I couldn't find the answer to that question in the provided notebook sources.

### Q6 [rerank]: What is the professor's favorite color?

**Expected:** Not in the sources; should say it can't find it

**Retrieved chunks:**

1. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 2* (score -11.3336): 1.   Extract   the   text   2.   Split   the   text   into   chunks   3.   Generate   embeddings   4.   Store   the   embeddings   in   a   vector   database   5.   Associate   the   content   with   ...
2. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 1* (score -11.3817): Project:   NotebookLM/Gemini   Notebook   Clone   Project   Goal   Build   a   full-stack   AI   application   that   allows   users   to   create   multiple   notebooks,   upload   or   link   source...
3. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 3* (score -11.3827): the   deployment   environment   has   limitations   on   persistent   storage,   document   those   limitations   rather   than   trying   to   solve   them   with   unnecessary   infrastructure.  5....
4. *5010 Project_ NotebookLM_Gemini Notebook Clone.pdf, page 8* (score -11.3871): tools .   However,   you   should   first   establish   the   application   design/specification   before   generating   the   implementation.  12.   Advanced   Features   —   Optional   The   followi...

**Answer** (7.07s):

I couldn't find the answer in this notebook's sources.


## Conclusions
**Answer quality.** Both methods answered all six questions correctly and grounded their answers in the source. Reranking scored a little higher on average (4.8 vs 4.5 out of 5, judged by the LLM). The two biggest differences were Q3 and Q6. For Q3 (what the demo should show), plain vector search ranked the general Deliverables page first, while reranking moved the page that actually lists the demo steps (page 6) to the top. For Q6 (a question the PDF can't answer), both methods correctly said the answer wasn't in the sources, but the reranker made it much clearer: every chunk scored around -11, a strong signal that nothing relevant exists. On easy questions with obvious keywords (Q2, Q5), both methods picked nearly the same chunks and gave the same answer.

**Speed and tradeoffs.** Reranking made retrieval about 20x slower (0.51s vs 0.02s on average), because the cross-encoder has to score 20 candidate chunks one by one. In practice this didn't matter, since total response time is dominated by the LLM call (5 to 9 seconds here, partly due to Groq free-tier rate limits). The averages were 5.3s for rerank and 5.8s for vector, so the difference is within normal LLM variation. The real costs of reranking are a second model to load (more memory and a slower first request after a cold start) and slightly more CPU per question.

**Choice.** I chose reranking as the default because it puts the most relevant chunk first more often, handles "not in the sources" questions more clearly, and costs only about half a second. Plain vector search is still available in the UI and is a good choice when speed matters more than precision. One limitation of this evaluation is that it uses a single document and an LLM judge, so the quality scores are approximate. A larger test with several documents and human-graded answers would give a stronger comparison.