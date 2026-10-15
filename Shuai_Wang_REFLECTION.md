# Engineering Reflection for Census Analytics Agent

## 1. Before the Assignment: Establishing a Reliable Development Environment

Given the 24-hour constraint, I prepared a reusable development environment in advance to minimize setup overhead and reserve the assignment period for problem analysis, engineering decisions, and implementation.

Before receiving the assignment, I configured a remote Linux server, initialized a GitHub repository, and established a Codex-assisted development workflow. I also prepared project-level instructions and reusable skills covering coding standards, architecture, testing, and version control. I verified the development workflow to ensure that implementation and testing could begin without unnecessary delays.

Upon receiving the assignment, I identified the resources required for delivery, including a Snowflake Trial account, Census Marketplace data, LLM inference capabilities, and public hosting. I also considered credential protection, database permissions, resource quotas, and the security implications of public access.

## 2. During the Assignment: Requirement Decomposition, Architectural Decisions, and Iterative Development

### 2.1 Translating Open-Ended Requirements into an Executable Plan

Rather than immediately asking Codex to implement an agent, I first analyzed the assignment requirements and identified the capabilities needed for successful delivery.

The application needed to support grounded Census queries, multi-turn conversations, statistically meaningful answers, ambiguity handling, a 60-second response limit, and public web access. It also needed to meet the reliability standards expected of software delivered to a customer.

I translated these requirements into functional and non-functional objectives, prioritizing them by technical dependencies, delivery risk, and evaluation importance. Reliable data access, statistical correctness, multi-turn interaction, and public availability were essential. Broader metadata coverage, systematic evaluation, failure recovery, and performance optimization were incorporated into the reliability objectives, while advanced statistical operations and interface enhancements were deferred.

I organized implementation into five stages:

1. **Data Grounding:** Explore Census schemas and metadata and construct a searchable semantic catalog.
2. **Core Conversational Agent:** Implement intent interpretation, indicator selection, validated SQL execution, and multi-turn interaction.
3. **Reliability and Evaluation:** Establish execution safeguards, failure handling, resource controls, and independent evaluation.
4. **Web Deployment:** Deliver an authenticated public application and validate its behavior in the deployed environment.
5. **Finalization:** Consolidate evaluation evidence, documentation, repository contents, and submission materials.

Each stage had defined objectives, constraints, and acceptance criteria. I used Codex for implementation and testing, reviewed execution evidence, and preserved verified checkpoints through Git.

I treated the plan as adaptable rather than fixed. When data exploration, evaluation, or deployment revealed new issues, I reassessed priorities and adjusted subsequent tasks. This allowed me to accelerate implementation with AI tools while retaining control over architecture, validation, and delivery.

### 2.2 Choosing a Data-Grounded Architecture

My first technical decision was to understand the Census dataset before selecting an agent architecture.

The dataset contains thousands of statistical indicators across different population universes, geographic levels, reporting periods, and statistical products. I recognized that the main challenge was not merely generating valid SQL, but ensuring that the selected indicators and calculations represented the user's question correctly. A query can execute successfully and return a real value while still answering the wrong question.

I therefore adopted a metadata-grounded approach rather than unrestricted text-to-SQL. I constructed a semantic catalog covering 59 statistical tables and 16,878 physical indicator fields, of which 16,582 had available definitions. The remaining 296 insufficiently defined fields were excluded from automatic interpretation rather than assigned speculative meanings.

I selected a **single-agent architecture with a constrained execution workflow**. Snowflake Cortex handles natural-language interpretation and structured intent planning, while deterministic Python components validate indicators, geographic constraints, and statistical operations, compile controlled SQL, and ground responses in actual query results.

I avoided unrestricted LLM-generated SQL and multi-agent orchestration because the application had a well-defined data source and execution path. Additional agent coordination would introduce latency, complexity, and failure points without a clear benefit under the 60-second constraint. Separating probabilistic interpretation from deterministic execution also made the system easier to test, debug, and inspect.

For example, population counts may be aggregated under valid conditions, whereas medians, ratios, and margins of error cannot be combined arbitrarily. When the data cannot support a defensible calculation, the application explains the limitation rather than returning a potentially misleading result.

### 2.3 Organizing AI-Assisted Implementation and Review

I used Codex for code implementation, test development, debugging, and documentation, and Muse as a secondary AI assistant for supplementary code review, Snowflake configuration, and operational checks.

Rather than delegating the assignment to a single agent, I defined bounded tasks with explicit completion criteria and required execution evidence wherever applicable. I separated implementation, review, and acceptance, evaluating AI-generated recommendations through tests, database outputs, and deployed behavior rather than treating generated explanations as verification.

This was especially important for database privileges, service configuration, resource management, and performance decisions. The effectiveness of AI-assisted development depended not only on implementation speed, but also on task clarity, acceptance criteria, and feedback between iterations.

### 2.4 Integrating Evaluation into Development

I incorporated testing throughout development rather than postponing it until the application was complete.

Tests covered metadata retrieval, geographic resolution, statistical rules, SQL validation, conversational state, and simulated model or database failures. For factual questions, I used independently constructed reference SQL against Snowflake data to verify numerical results, rather than relying on another LLM to judge whether an answer appeared plausible.

After establishing core functionality, I introduced a separate evaluation set distinct from the initial development examples. It tested unfamiliar question formulations, indicator selection, follow-up questions, and cases where the data did not justify an answer.

This layered approach helped identify whether failures originated from retrieval, intent interpretation, conversation state, statistical validation, or execution, allowing subsequent improvements to target the relevant component.

## 3. After Implementation: Validation, Performance Optimization, and Lessons Learned

### 3.1 Learning from Independent Evaluation

The first independent evaluation passed **19 of 25 cases**.

Failures revealed subtle semantic issues, including incorrect household-related indicators, misinterpreted housing tenure conditions, and unjustified selection of statistical sources when user requests were underspecified. Some queries returned valid database values but failed to answer the intended question.

I addressed these issues by improving indicator resolution, source ambiguity handling, and conversational constraint inheritance rather than simply adding prompt examples.

After these changes, the same evaluation set passed **25/25 regression cases**. I viewed this as evidence that the identified failures had been addressed, not as an estimate of accuracy on unseen questions.

This evaluation reinforced an important lesson: a numerically valid answer is not necessarily a statistically or contextually correct one.

### 3.2 Diagnosing and Improving Real-World Performance

After implementation, I deployed the application to an independent server with HTTPS access and tested authentication, factual queries, multi-turn interactions, unsupported requests, rate limits, and restart recovery.

I also evaluated the application directly as a user, paying attention to latency, conversation continuity, and error handling.

Rather than immediately increasing Snowflake Warehouse resources, I profiled the execution pipeline. A representative SQL query required approximately 0.28 seconds, while model inference, connection initialization, and repeated metadata-index preparation contributed more substantially to latency.

I optimized metadata-index preparation and loading and reduced redundant resource-cleanup operations. The measured response time improved from approximately **15.03 seconds to 12.99 seconds**.

This experience reinforced the value of identifying actual bottlenecks before investing in additional infrastructure or architectural complexity.

### 3.3 Lessons Learned and Future Improvements

Looking back, the most effective decision was organizing an open-ended assignment into prioritized stages with clear dependencies and acceptance criteria. This allowed me to use Codex efficiently while maintaining control through regular verification and version management. Muse provided additional perspectives through supplementary review and operational checks.

Another important lesson was that reliable AI agents depend on more than model capabilities. Understanding data semantics, defining execution boundaries, and designing meaningful evaluations were equally important. The independent evaluation was particularly valuable in revealing errors that successful demonstrations alone would not have exposed.

If I were to undertake a similar assignment again, I would introduce real-user testing and end-to-end performance profiling earlier, and prepare deployment in parallel with agent development. I would also refine the collaboration between AI tools to make implementation, cross-review, and verification more efficient.

For the application itself, I would prioritize broader independent evaluation, expanded statistically validated query capabilities, and stronger access controls, monitoring, and concurrency management.

Overall, this assignment reinforced the value of combining deliberate engineering judgment with AI-assisted implementation: translating ambiguous requirements into clear decisions, validating results with evidence, and delivering a functional, dependable application under practical constraints.
