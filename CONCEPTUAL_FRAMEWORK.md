## SME IT Project Risk Management: Conceptual Framework

### Overview
A practical, lightweight framework tailored for SMEs to manage IT project risks with iterative feedback loops.

### Phases and Activities
1. Identification
   - Capture risks from scope, schedule, cost, quality, resources, dependencies, and technology.
   - Inputs: project parameters (size, budget, duration, team experience), contextual notes.
2. Evaluation
   - Qualitative scoring: Likelihood (1–5), Impact (1–5).
   - Derived features: complexity, churn, dependency count.
   - Manual baseline: RiskScore = Likelihood × Impact; categories: Low/Medium/High.
3. Prioritization
   - Rank by RiskScore and AI-predicted level; visualize heatmaps and priority matrices.
   - Assign ownership and target dates.
4. Control & Monitoring
   - Periodic re-assessment; track deltas and trend outliers.
   - Feedback loop: update parameters, re-score, collect usability/peer feedback.

### Feedback Loops
- Re-score on parameter change or new data upload.
- Capture usability feedback and supervisor review; revise thresholds/features.
- Benchmark framework fit (ISO 31000, PMBOK, PRINCE2) and tailor practices accordingly.

### Tailoring Principles (SME-Oriented)
- Simplicity first: minimal mandatory fields; optional advanced metrics.
- Scalability: start with qualitative matrix; add ML when data grows.
- Documentation-light: auto-generated tables/visuals serve as artefacts.
- Applicability to IT: include technical complexity, dependencies, and change indicators.

### Roles & Responsibilities
- Project Manager: owns risk register, initiates re-assessment.
- Team Leads: supply feature/complexity inputs and mitigation actions.
- Stakeholders: review visualizations and approve responses.

### Acceptance Criteria
- Usability: clear inputs, 1–2 click analysis, printable report.
- Functionality: correct composite scores, consistent visuals, basic error handling.
- Adaptability: configurable thresholds, optional fields, benchmark-guided tailoring.


