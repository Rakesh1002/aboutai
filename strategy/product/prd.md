# Product Requirements Document (PRD): aboutai

<table>
  <tr>
   <td><strong>Document Details</strong>
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td><strong>Project Name</strong>
   </td>
   <td>aboutai (The "Trust Engine" Platform)
   </td>
  </tr>
  <tr>
   <td><strong>Version</strong>
   </td>
   <td>1.0 - Alpha Phase
   </td>
  </tr>
  <tr>
   <td><strong>Status</strong>
   </td>
   <td><strong>Draft / Engineering Review</strong>
   </td>
  </tr>
  <tr>
   <td><strong>Primary Goal</strong>
   </td>
   <td>To build the definitive source of truth for the AI economy by automating technical vetting and vertical intelligence.
   </td>
  </tr>
</table>

---

## 1. Executive Summary & Core Value Proposition

**aboutai** is a multi-modal platform combining a verified tool directory, investigative news, and educational cohorts. Unlike existing aggregators that rely on user submissions or basic scraping, 'aboutai' utilizes an **Autonomous Agentic Vetting System** to test, score, and monitor AI tools for utility, hallucination rates, and "wrapper" dependency.

**The "North Star" Metric:** **verified_deployments** (The number of times a user adopts a tool _after_ viewing a Trust Score).

---

## 2. User Personas

1. **The Enterprise Pragmatist (Primary Buyer):** CTOs/CIOs in legacy industries (AgTech, Manufacturing).
   - _Pain Point:_ Cannot distinguish between a demo that works and a "wrapper" that breaks. Needs audit trails.
   - _Feature Need:_ "Trust Score," compliance checks, API stability monitoring.
2. **The Vertical Implementer:** SMB owners (e.g., a law firm partner).
   - _Pain Point:_ Overwhelmed by generic tools. Needs specific legal AI.
   - _Feature Need:_ Vertical-specific content desks, cohort courses.
3. **The AI Engineer (Builder):**
   - _Pain Point:_ Needs distribution to high-quality users, not just "free trial" seekers.
   - _Feature Need:_ Verified listing status, technical feedback loops.

---

## 3. Functional Requirements

### 3.1 Module A: The Directory & "Trust Engine"

The core differentiator. This system automatically ingests, tests, and scores tools.

<table>
  <tr>
   <td><strong>ID</strong>
   </td>
   <td><strong>Feature</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Priority</strong>
   </td>
   <td><strong>Technical Ref</strong>
   </td>
  </tr>
  <tr>
   <td><strong>FR-01</strong>
   </td>
   <td><strong>Ingestion Pipeline</strong>
   </td>
   <td>Automated scraping of GitHub, Product Hunt, and user submissions. Must extract: Tech stack, API endpoints, Documentation URL.
   </td>
   <td>P0
   </td>
   <td><sup>1</sup>
   </td>
  </tr>
  <tr>
   <td><strong>FR-02</strong>
   </td>
   <td><strong>Wrapper Detection</strong>
   </td>
   <td>Algorithm to analyze dependency on generic APIs (OpenAI/Anthropic) vs. proprietary infrastructure (Vector DBs, Custom Fine-tunes).
   </td>
   <td>P0
   </td>
   <td><sup>2</sup>
   </td>
  </tr>
  <tr>
   <td><strong>FR-03</strong>
   </td>
   <td><strong>Agentic Testing Loop</strong>
   </td>
   <td>A fleet of "Tester Agents" that execute standard prompts against the tool's API and grade the output for hallucination and latency.
   </td>
   <td>P0
   </td>
   <td>[<sup>10</sup>],
   </td>
  </tr>
  <tr>
   <td><strong>FR-04</strong>
   </td>
   <td><strong>Trust Score Calc</strong>
   </td>
   <td>Composite score (0-100) based on: Reliability, Transparency, Latency, and Proprietary Value.
   </td>
   <td>P0
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td><strong>FR-05</strong>
   </td>
   <td><strong>Live Monitoring</strong>
   </td>
   <td>Periodic "health checks" to ensure the tool hasn't become "zombieware" (broken/abandoned).
   </td>
   <td>P1
   </td>
   <td>
   </td>
  </tr>
</table>

### 3.2 Module B: The News & Intelligence Platform

A CMS-driven news aggregator enhanced by AI analysis.

<table>
  <tr>
   <td><strong>ID</strong>
   </td>
   <td><strong>Feature</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Priority</strong>
   </td>
   <td><strong>Technical Ref</strong>
   </td>
  </tr>
  <tr>
   <td><strong>FR-06</strong>
   </td>
   <td><strong>Hype Meter</strong>
   </td>
   <td>NLP analysis of news articles to detect sensationalism (e.g., usage of words like "Revolutionary," "AGI," "Magic").
   </td>
   <td>P1
   </td>
   <td><sup>3</sup>
   </td>
  </tr>
  <tr>
   <td><strong>FR-07</strong>
   </td>
   <td><strong>Vertical Feeds</strong>
   </td>
   <td>Dynamic filtering of content into silos: AgTech, Legal, DevTools, Manufacturing.
   </td>
   <td>P1
   </td>
   <td><sup>4</sup>
   </td>
  </tr>
  <tr>
   <td><strong>FR-08</strong>
   </td>
   <td><strong>Daily Brief Generator</strong>
   </td>
   <td>Automated summarization of top 50 daily links into a newsletter draft for human editorial review.
   </td>
   <td>P2
   </td>
   <td><sup>5</sup>
   </td>
  </tr>
</table>

### 3.3 Module C: Community & Accounts

<table>
  <tr>
   <td><strong>ID</strong>
   </td>
   <td><strong>Feature</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Priority</strong>
   </td>
   <td><strong>Technical Ref</strong>
   </td>
  </tr>
  <tr>
   <td><strong>FR-09</strong>
   </td>
   <td><strong>Verified Profiles</strong>
   </td>
   <td>SSO Integration (GitHub/LinkedIn). Badging for users who have completed cohorts.
   </td>
   <td>P2
   </td>
   <td><sup>6</sup>
   </td>
  </tr>
  <tr>
   <td><strong>FR-10</strong>
   </td>
   <td><strong>Cohort LMS</strong>
   </td>
   <td>Integration with a cohort platform (or custom build) for live course management (syllabus, calendar, Zoom links).
   </td>
   <td>P2
   </td>
   <td><sup>7</sup>
   </td>
  </tr>
</table>

---

## 4. Technical Architecture & Specifications

### 4.1 High-Level Stack

- **Frontend:** Next.js (App Router) deployed on Vercel. React Server Components for SEO performance.
- **Backend API:** Python (FastAPI) for the Agentic Orchestration Layer.
- **Database:** Supabase (PostgreSQL) + pgvector (for semantic search of tools).
- **Queue/Async:** Redis (via BullMQ) to handle long-running agent testing tasks.
- **Orchestration:** LangChain / LangGraph for defining agent workflows.

### 4.2 The "Trust Engine" Algorithm (Specification)

**Objective:** Automatically generate a trust_score (0-100).

Algorithm Logic:

The score is a weighted average of four vectors:

$$TrustScore = (w_1 \cdot P_{tech}) + (w_2 \cdot R_{test}) + (w_3 \cdot T_{trans}) + (w_4 \cdot L_{life})$$

1. **$P_{tech}$ (Proprietary Tech Score):**
   - Scans package.json or requirements.txt (if open source) or analyzes API latency patterns.
   - _Heuristic:_ High correlation with standard OpenAI API latency curves = Low Score (likely a wrapper). presence of pinecone, weaviate, or custom model weights = High Score.
2. **$R_{test}$ (Reliability Score):**
   - Agent executes 5 test prompts.
   - _Metric:_ Success Rate (Did it error?) + Hallucination Rate (checked against a "Ground Truth" LLM).
   - _Ref:_ (Accuracy, Precision, Recall).
3. **$T_{trans}$ (Transparency Score):**
   - Does the site have a "Team" page? Is pricing clear? Is there a privacy policy?
4. **$L_{life}$ (Liveness Score):**
   - Last commit date (GitHub) or Last blog post date.

**Agent Implementation (Python/LangChain Snippet):**

    Python

# Pseudo-code for the Vetting Agent Workflow \

from langchain.agents import AgentType, initialize_agent \
from langchain.tools import Tool \
 \
def analyze_wrapper_likelihood(url: str): \
 """ \
 Analyzes DOM and network requests to determine if a site is a thin wrapper. \
 """ \
 # 1. Headless browse (Browserbase/Puppeteer) \
 # 2. Capture API calls \
 # 3. Check for specific 'About' page disclosures \
 # Returns score 0.0 to 1.0 \
 pass \
 \
def functional_test(tool_name: str, test_prompt: str): \
 """ \
 Uses an LLM to act as a user and test the tool. \
 """ \
 # 1. Agent navigates to tool \
 # 2. Agent inputs 'test_prompt' \
 # 3. Agent captures output \
 # 4. 'Grader Agent' evaluates output quality \
 pass \
 \

# Main Workflow \

def calculate_trust_score(tool_data): \
 tech_score = analyze_wrapper_likelihood(tool_data['url']) \
 reliability = functional_test(tool_data['name'], "Generate a python script for...") \
 \
 final_score = (tech_score _ 0.4) + (reliability _ 0.4) + (tool_data['transparency'] \* 0.2) \
 return final_score \

### 4.3 Database Schema (Supabase/PostgreSQL)

**Table: tools**

- id (UUID, PK)
- name (Text)
- slug (Text, Unique)
- vertical (Enum: 'AgTech', 'Legal', 'Dev', 'Marketing')
- is_wrapper (Boolean, Flagged by Agent)
- trust_score (Integer, 0-100)
- pricing_model (JSONB)
- last_audited_at (Timestamp)

**Table: audit_logs**

- id (UUID, PK)
- tool_id (FK)
- agent_version (Text)
- test_prompt (Text)
- tool_response (Text)
- hallucination_detected (Boolean)
- latency_ms (Integer)

**Table: news_items**

- id (UUID, PK)
- source_url (Text)
- hype_score (Integer)
- vertical_tags (Array)

---

## 5. UI/UX Requirements

### 5.1 The "Wrapper Detector" (Homepage Feature)

- **Input:** Single text field (URL).
- **Action:** User clicks "Analyze".
- **Output:** A "Nutrition Label" style modal.
  - _Proprietary Tech:_ High/Medium/Low
  - _Risk Level:_ Green/Yellow/Red
  - _Verdict:_ "Likely a Wrapper" or "Native AI Application"

### 5.2 The Listing Page

- **Visual Hierarchy:** The TrustScore must be the most prominent element, placed above the "Visit Website" button.
- **Evidence Locker:** A tab showing the raw logs of the Agentic Audit (e.g., "See how our agent tested this tool"). This builds radical transparency.<sup>8</sup>

---

## 6. Integrations & Third-Party Services

- **Authentication:** Clerk or Supabase Auth.
- **Payments:** Stripe (for "Deep Audit" expedited reviews and Cohorts).
- **Community Platform:** Circle.so (via API for SSO and member syncing).<sup>6</sup>
- **Email:** Beehiiv API (for newsletter syncing).<sup>9</sup>
- **Search:** Algolia (for fast, typo-tolerant search of the directory).

---

## 7. Roadmap & Phasing

### Phase 1: The Crawler & Database (Weeks 1-4)

- Set up Supabase schema.
- Build Python scrapers for Product Hunt/GitHub.
- Implement basic "Wrapper Detection" heuristic (v1).
- **Deliverable:** Internal database with 1,000 tools.

### Phase 2: The MVP Directory (Weeks 5-8)

- Build Next.js frontend.
- Deploy "Wrapper Detector" public tool.
- Launch Beehiiv newsletter.
- **Deliverable:** Public launch of aboutai.com with core directory.

### Phase 3: The Trust Engine Activation (Weeks 9-12)

- Deploy the full "Agentic Testing" pipeline (LangChain integration).
- Begin publishing "Audit Logs" on tool pages.
- **Deliverable:** TrustScore goes live on all listings.

### Phase 4: Vertical Expansion (Weeks 13+)

- Launch "AgTech" and "Legal" specific sub-domains.
- Open cohort enrollment.

#### Works cited

1. How to Build an LLM Agent With AutoGen: Step-by-Step Guide - Neptune.ai, accessed on November 27, 2025, [https://neptune.ai/blog/building-llm-agents-with-autogen](https://neptune.ai/blog/building-llm-agents-with-autogen)
2. Stop Building AI Wrappers - by Mustafa Kapadia - The AI Empowered Product Manager, accessed on November 27, 2025, [https://mustafakapadia.substack.com/p/stop-building-ai-wrappers](https://mustafakapadia.substack.com/p/stop-building-ai-wrappers)
3. Tow Report: "Artificial Intelligence in the News" and How AI Reshapes Journalism and the Public Arena, accessed on November 27, 2025, [https://journalism.columbia.edu/news/tow-report-artificial-intelligence-news-and-how-ai-reshapes-journalism-and-public-arena](https://journalism.columbia.edu/news/tow-report-artificial-intelligence-news-and-how-ai-reshapes-journalism-and-public-arena)
4. The State of AI 2025 - Bessemer Venture Partners, accessed on November 27, 2025, [https://www.bvp.com/atlas/the-state-of-ai-2025](https://www.bvp.com/atlas/the-state-of-ai-2025)
5. Create Your Personalized News Digest Using AI Agents - Analytics Vidhya, accessed on November 27, 2025, [https://www.analyticsvidhya.com/blog/2024/09/personalized-news-digest/](https://www.analyticsvidhya.com/blog/2024/09/personalized-news-digest/)
6. 20 Best Online Community Platforms (UPDATED 2025 Rankings + Top 5) | Mighty Networks, accessed on November 27, 2025, [https://www.mightynetworks.com/resources/community-platforms](https://www.mightynetworks.com/resources/community-platforms)
7. How to Create a Cohort-Based Course - Kajabi Help Center, accessed on November 27, 2025, [https://help.kajabi.com/en/articles/12695118-how-to-create-a-cohort-based-course](https://help.kajabi.com/en/articles/12695118-how-to-create-a-cohort-based-course)
8. The CIO's Guide to Avoid AI-Washing: 9 Tips for Vetting AI Vendors and Solutions, accessed on November 27, 2025, [https://www.ondemandgroup.com/the-cios-guide-to-avoid-ai-washing-9-tips-for-vetting-ai-vendors-and-solutions/](https://www.ondemandgroup.com/the-cios-guide-to-avoid-ai-washing-9-tips-for-vetting-ai-vendors-and-solutions/)
9. How to Monetize Your Newsletter & Website in 2025 - YouTube, accessed on November 27, 2025, [https://www.youtube.com/watch?v=oQg3V7VYBhc](https://www.youtube.com/watch?v=oQg3V7VYBhc)
10. AI Agents in Java: Automating Non-Functional Requirements for Secure, Scalable Apps, accessed on November 27, 2025, [https://medium.com/@dfs.techblog/ai-agents-in-java-automating-non-functional-requirements-for-secure-scalable-apps-9ea77f9b9485](https://medium.com/@dfs.techblog/ai-agents-in-java-automating-non-functional-requirements-for-secure-scalable-apps-9ea77f9b9485)
