# Girl Dropout Analysis Guide

## Goal
Build a minister-ready, self-readable slide deck explaining why girl dropout happens, how it varies by state, which policy levers matter most, and what the future looks like if nothing changes.

## Who This Is For
This is written for an Additional Secretary, Secretary, or Minister-level audience.

That means the deck should answer three questions quickly:
1. What is the problem?
2. What drives it?
3. What should the government do next?

## Better Questions To Answer
Your original questions are good, but they can be reframed into a sharper policy flow.

### 1. Where is the problem most severe?
- Which states, districts, or school stages have the highest girl dropout rates?
- Is the issue concentrated in upper primary, secondary, or higher secondary?
- Is the pattern getting better or worse over time?

### 2. What explains the variation?
- Which factors are most correlated with girl dropout across states?
- Is dropout more associated with access, quality, safety, poverty, or transition points?
- Are the drivers the same everywhere, or do they differ by state group?

### 3. Which levers can the government actually control?
- School access and distance
- Availability of girls’ toilets and water
- Female teacher share
- Transition support and retention initiatives
- School density in rural areas
- Transport, hostels, and safety-related support
- Scholarship / incentive coverage

### 4. What happens if nothing changes?
- What is the expected dropout trend if current patterns continue?
- Which states are likely to improve naturally, and which will stagnate?
- How big is the gap between business-as-usual and a realistic improvement scenario?

### 5. What should a Secretary do next?
- Which 3–5 interventions should be prioritized?
- Which states should get differentiated action plans?
- What metrics should be tracked quarterly?

## Data Sources
Use public official data first.

### Primary
- UDISE+ state and district report cards
- Historical DISE/UDISE series for continuity where available

### Possible Supporting Sources
- Census / population context for child population and rural share
- NFHS indicators for household and girls’ education context
- State education dashboards, if official and comparable
- Ministry / state scholarship or infrastructure data, if available

## What To Download
Try to build a panel with one row per state-year, and if possible district-year.

Minimum fields to look for:
- Girl dropout rate by stage
- Enrollment by gender and stage
- Girls’ toilet availability
- Drinking water availability
- Electricity
- Pupil-teacher ratio
- Female teacher share
- School access / habitation coverage
- Transition rates between stages
- School type and rural/urban split

## Analysis Approach

### Step 1: Define the outcome
Use girl dropout rate as the main outcome.

If available, split by stage:
- Primary
- Upper primary
- Secondary
- Higher secondary

This is important because the policy lever is often different at each stage.

### Step 2: Describe the geography
Create three views:
- India-wide trend over time
- State ranking in the latest year
- Heatmap of state-by-year change

### Step 3: Find likely drivers
Start with simple, transparent analysis before any complex model:
- Correlation matrix
- State fixed-effects regression or panel regression
- Feature importance from a tree model, if the data is large enough

Important: do not present correlation as causation. For the minister deck, use the word “associated with,” not “causes,” unless the analysis is truly causal.

### Step 4: Segment states
Create state archetypes such as:
- High dropout, low infrastructure
- High dropout, high access but weak retention
- Low dropout, strong infrastructure
- Improving fast vs stuck states

This is often more useful than one all-India average.

### Step 5: Build a status-quo forecast
Use a simple forecast first:
- Trend extrapolation by state
- Scenario without intervention
- Optional: state-level panel forecast

Then compare it with a realistic improvement scenario.

## How To Think About “Biggest Lever”
Do not answer only with the strongest statistical coefficient.

For policy, the biggest lever is the one that is:
1. Strongly associated with lower dropout
2. Controllable by the state government
3. Feasible to improve within 12–24 months
4. Measurable in administrative data

That usually means you should rank levers using two lenses:
- Statistical impact
- Implementation feasibility

## Slide Deck Structure
Use about 8–12 slides.

1. Title and one-line takeaway
2. Why girl dropout matters now
3. Where the problem is worst
4. How it varies by state and stage
5. What drives dropout in the data
6. Which levers matter most and are controllable
7. What happens if we do nothing
8. What a differentiated state action plan looks like
9. Recommended priorities for the next 12 months
10. Appendix with methods and data sources

## What The Final Story Should Say
A strong minister-level narrative usually looks like this:

- Girl dropout is not uniform; it is concentrated in specific states and school stages.
- Infrastructure alone is not enough, but certain basics matter a lot.
- The biggest gains usually come from combining access, safety, retention support, and transition management.
- Some states need infrastructure fixes, others need retention and transition fixes.
- If we do nothing, some improvement may continue, but the highest-risk states will remain stuck.

## Deliverable Checklist For Tomorrow
- Download and organize UDISE+/DISE data
- Build one clean analysis table
- Produce the top 5 charts
- Write 5 key findings in plain English
- Convert those findings into 3 policy recommendations
- Draft the slide deck narrative

## Practical Warning
If the public data is only aggregated and not microdata, you can still do a strong policy analysis.

In that case, focus on:
- State and district variation
- Time trends
- Infrastructure and access indicators
- Scenario forecasts

That is enough for a convincing ministerial deck.