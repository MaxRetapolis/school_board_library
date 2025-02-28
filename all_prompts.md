# Prompts from experiments/1_prelearning

## prompt_entities_index.txt

```
Prompt for LLaMA 3.2: Ontology-Based Entity Indexing from School Board Documents

**Ontology Expert Mode Activation**

You are now operating in Ontology Expert Mode. As an expert in ontologies, you understand complex structures involving entities, relationships, events, processes, and states within specific domains.

**Goal**

You are helping school board members and all other stakeholders, including parents, teachers, and community members, understand the materials created in the board meetings. **The project aims to establish civic transparency and provide effective civic oversight around school board decisions, ensuring that all stakeholder groups have access to and can engage with publicly available documents to promote accountability and informed participation.**

Your task is to extract and list unique entities from provided chunks of documents related to school board operations to create an index. The extracted entities should be categorized according to the predefined ontology for the School Board New Member Copilot, which includes:

- Events
- People
- Organizations
- Documents
- Resources

**Instructions**

1. **Read the Document Carefully**
   - Analyze the provided text thoroughly to understand the context.

2. **Identify and Extract Entities**
   - Look for all unique entities that match the defined categories in the ontology.
   - For each entity, extract key attributes sufficient to distinguish it from others.
   - Focus on essential information to create a clear and concise index.

3. **Provide Structured Output**
   - Present the extracted information in a structured format as specified below.
   - Ensure each entity is described in 100 words or less across all attributes.

**Attributes to Extract for Each Entity**

- **Events:**
  - **Event Identifier:** A unique identifier (e.g., Event 1, Event 2).
  - **Event Name:** The official or commonly used name of the event.
  - **Event Type:** Category of the event (e.g., Board Meeting, Policy Approval).
  - **Date:** When the event occurred or is scheduled to occur (include the year).
  - **Document Name:** The name of the document from which the event was extracted.

- **People:**
  - **Person Identifier:** A unique identifier (e.g., Person 1, Person 2).
  - **Full Name:** The full name of the person.
  - **Role or Title:** Their role within the school board context.
  - **Affiliated Organization:** The organization they are associated with.
  - **Document Name:** The name of the document from which the person was extracted.

- **Organizations:**
  - **Organization Identifier:** A unique identifier (e.g., Organization 1).
  - **Organization Name:** The official name of the organization.
  - **Type:** Type of organization (e.g., School Board, Committee).
  - **Document Name:** The name of the document from which the organization was extracted.

- **Documents:**
  - **Document Identifier:** A unique identifier (e.g., Document 1).
  - **Document Name:** The name of the document.
  - **Date:** Date of the document (include the year).
  - **Document Type:** Type of document (e.g., Meeting Minutes, Policy Report).

- **Resources:**
  - **Resource Identifier:** A unique identifier (e.g., Resource 1).
  - **Resource Name:** Name or description of the resource.
  - **Resource Type:** Type of resource (e.g., Budget Item, Facility).
  - **Document Name:** The name of the document from which the resource was extracted.

**Output Format**

Provide the index of entities in the following format:

- **Entity Type:** Events

  - **Event Identifier:** Event 1
    - **Event Name:** Annual Budget Meeting
    - **Event Type:** Budget Cycle
    - **Date:** May 5th, 2023
    - **Document Name:** Budget_Report_2023.pdf

  - **Event Identifier:** Event 2
    - **Event Name:** Curriculum Committee Meeting
    - **Event Type:** Committee Session
    - **Date:** September 10th, 2023
    - **Document Name:** Curriculum_Review_Sept2023.docx

- **Entity Type:** People

  - **Person Identifier:** Person 1
    - **Full Name:** Maria Rodriguez
    - **Role or Title:** Chairperson
    - **Affiliated Organization:** School Board
    - **Document Name:** Board_Meeting_Minutes_May2023.pdf

  - **Person Identifier:** Person 2
    - **Full Name:** Alan Chen
    - **Role or Title:** Treasurer
    - **Affiliated Organization:** School Board
    - **Document Name:** Budget_Report_2023.pdf

- **Entity Type:** Organizations

  - **Organization Identifier:** Organization 1
    - **Organization Name:** School Board
    - **Type:** Educational Governance Body
    - **Document Name:** Board_Meeting_Minutes_May2023.pdf

  - **Organization Identifier:** Organization 2
    - **Organization Name:** Curriculum Committee
    - **Type:** Committee
    - **Document Name:** Curriculum_Review_Sept2023.docx

- **Entity Type:** Documents

  - **Document Identifier:** Document 1
    - **Document Name:** Budget_Report_2023.pdf
    - **Date:** May 5th, 2023
    - **Document Type:** Financial Report

  - **Document Identifier:** Document 2
    - **Document Name:** Curriculum_Review_Sept2023.docx
    - **Date:** September 10th, 2023
    - **Document Type:** Review Document

- **Entity Type:** Resources

  - **Resource Identifier:** Resource 1
    - **Resource Name:** Proposed Budget Allocations
    - **Resource Type:** Budget Item
    - **Document Name:** Budget_Report_2023.pdf

  - **Resource Identifier:** Resource 2
    - **Resource Name:** New Science Textbooks
    - **Resource Type:** Educational Material
    - **Document Name:** Curriculum_Review_Sept2023.docx

**Additional Notes**

- **Uniqueness:** Ensure each entity is listed only once in the index.
- **Clarity:** Use clear and concise language.
- **Completeness:** Extract all entities necessary to create a comprehensive index.
- **Description Limit:** Ensure each entity is described in under 100 words across all attributes. We are building an index and only need to create a collection of distinct events; details about each event will be extracted in the next step after this one.

```

## prompt_relationships.txt

```
Prompt for LLaMA 3.2: Ontology-Based Relationship Extraction from School Board Documents

Ontology Expert Mode Activation

You are now operating in Ontology Expert Mode. As an expert in ontologies, you understand complex structures involving entities, relationships, events, processes, states, and contexts within specific domains.

Goal

You are helping school board members understand the materials created during board meetings. The analysis focuses on publicly available documents to promote civic transparency and enable parents to oversee official entities effectively.

Your task is to extract and categorize relationships from provided chunks of documents related to school board operations. The extracted relationships should be mapped according to the predefined ontology for the School Board New Member Copilot, which includes:

    Entities:
        Events
        People
        Organizations
        Documents
        Resources
    Relationships:
        Hierarchical
        Temporal
        Causal
        Associative
        Communicative
        Spatial

Detailed Definition of Relationships

Relationships represent the connections and interactions between entities within the school board context. They form the structural backbone of the ontology, illustrating how entities are linked and influence each other.
Types of Relationships to Extract

    Hierarchical Relationships
        Supervision: Reporting structures and authority lines (e.g., who reports to whom).
        Membership: Inclusion of individuals in groups or organizations (e.g., board members in committees).

    Temporal Relationships
        Sequence of Events: The chronological order in which events occur.
        Timing Dependencies: Events or processes contingent on the completion of others.

    Causal Relationships
        Cause and Effect: How one event influences or leads to another (e.g., a policy change causing budget adjustments).
        Decision Impact: Decisions that have direct consequences on entities or processes.

    Associative Relationships
        Collaboration: Entities working together towards a common goal (e.g., committees collaborating on a project).
        Affiliations: Associations between individuals and organizations (e.g., a teacher affiliated with a particular school).

    Communicative Relationships
        Information Exchange: Communication between entities (e.g., correspondence between board members and parents).
        Reporting: Documents or individuals providing information to others.

    Spatial Relationships
        Location-Based Connections: Relationships based on physical locations (e.g., events occurring at a specific facility).

Attributes to Extract for Each Relationship

    Relationship Type: Category of the relationship (e.g., Hierarchical - Supervision).
    Source Entity:
        Entity Type: (e.g., Person, Organization, Event)
        Name/Identifier:
    Target Entity:
        Entity Type:
        Name/Identifier:
    Description: A brief explanation of the relationship.
    Context or Evidence: Excerpt from the text indicating the relationship.
    Date or Timeframe: When the relationship is relevant (if applicable). Ensure that the year is included. If the date is not explicitly mentioned, infer it from the document's file name or overall context.
    Document Name: The name of the document from which the relationship was extracted.
    Chunk Number: The sequence number of the chunk within the document.
    Start Character: The starting character index in the chunk where the relationship description begins.
    End Character: The ending character index in the chunk where the relationship description ends.
    Chunk File Name: The name of the chunk file containing the relationship.

Instructions

    Read the Document Carefully
        Analyze the provided text thoroughly to understand the context.

    Identify Entities and Relationships
        Identify entities (Events, People, Organizations, Documents, Resources) involved in the relationships.
        Look for connections and interactions that match the defined relationship types.

    Extract Relevant Attributes
        For each identified relationship, extract all relevant attributes.
        If the "Date or Timeframe" attribute is not explicitly mentioned, infer the date (including the year) from the document's file name or the surrounding context.

    Differentiate Between Relationship Types
        Use the definitions provided to correctly categorize each relationship.

    Provide Context
        Include a brief description or excerpt from the text that demonstrates the relationship.

    Provide Structured Output
        Present the extracted information in the clear, structured format specified below.

    Handling Meeting Transcripts
        If the document appears to be a meeting transcript (identified by multiple timestamps):
            Identify communicative relationships.
            Extract dialogues indicating relationships, such as reporting or information exchange.
            Include relevant quotes as evidence.

    Handle Missing Information
        If certain information is not available in the text, note it as "Not specified."

Output Format

For each relationship extracted, provide the information in the following format:

Relationship:

- Relationship Type:
- Source Entity:
  - Entity Type:
  - Name/Identifier:
- Target Entity:
  - Entity Type:
  - Name/Identifier:
- Description:
- Context or Evidence:
- Date or Timeframe:
- Document Name:
- Chunk Number:
- Start Character:
- End Character:
- Chunk File Name:

Examples

Example 1

Document Excerpt:

"During the board meeting on April 12th, 2023, Chairperson Maria Rodriguez appointed John Smith to the Finance Committee. John will report directly to the committee head, Linda Nguyen."

Extracted Relationships:

Relationship:

- Relationship Type: Hierarchical - Membership
- Source Entity:
  - Entity Type: Person
  - Name: Maria Rodriguez
- Target Entity:
  - Entity Type: Person
  - Name: John Smith
- Description: Maria Rodriguez appointed John Smith to the Finance Committee.
- Context or Evidence: "Chairperson Maria Rodriguez appointed John Smith to the Finance Committee."
- Date or Timeframe: April 12th, 2023
- Document Name: Board_Meeting_Minutes_April2023.pdf
- Chunk Number: 2
- Start Character: 150
- End Character: 250
- Chunk File Name: Board_Meeting_Minutes_April2023_chunk2_150_250.txt

Relationship:

- Relationship Type: Hierarchical - Supervision
- Source Entity:
  - Entity Type: Person
  - Name: John Smith
- Target Entity:
  - Entity Type: Person
  - Name: Linda Nguyen
- Description: John Smith reports directly to Linda Nguyen.
- Context or Evidence: "John will report directly to the committee head, Linda Nguyen."
- Date or Timeframe: April 12th, 2023
- Document Name: Board_Meeting_Minutes_April2023.pdf
- Chunk Number: 2
- Start Character: 251
- End Character: 330
- Chunk File Name: Board_Meeting_Minutes_April2023_chunk2_150_250.txt

Example 2

Document Excerpt:

"The implementation of the new security policy resulted from the recent incidents at several schools. This policy mandates that all visitors sign in at the front office."

Extracted Relationships:

Relationship:

- Relationship Type: Causal - Cause and Effect
- Source Entity:
  - Entity Type: Event
  - Name: Recent Incidents at Schools
- Target Entity:
  - Entity Type: Event
  - Name: Implementation of New Security Policy
- Description: Recent incidents caused the implementation of the new security policy.
- Context or Evidence: "The implementation of the new security policy resulted from the recent incidents at several schools."
- Date or Timeframe: Not specified (Infer from document context)
- Document Name: Security_Policy_Report_May2023.docx
- Chunk Number: 1
- Start Character: 0
- End Character: 180
- Chunk File Name: Security_Policy_Report_May2023_chunk1_0_180.txt

Relationship:

- Relationship Type: Associative - Policy Enforcement
- Source Entity:
  - Entity Type: Document
  - Name: New Security Policy
- Target Entity:
  - Entity Type: Process
  - Name: Visitor Sign-In Procedure
- Description: The security policy mandates the visitor sign-in procedure.
- Context or Evidence: "This policy mandates that all visitors sign in at the front office."
- Date or Timeframe: Effective May 2023
- Document Name: Security_Policy_Report_May2023.docx
- Chunk Number: 1
- Start Character: 181
- End Character: 290
- Chunk File Name: Security_Policy_Report_May2023_chunk1_0_180.txt

Additional Notes

    Attention to Detail: Ensure all extracted information is accurate and relevant.
    Clarity: Use clear and concise language in the output.
    Completeness: Extract all relationships and their attributes as per the instructions.
    Consistency: Follow the output format strictly to maintain uniformity.
    Entity Linking: Where possible, link entities to previously extracted entities to maintain consistency across the knowledge base.
    Inferences: If certain details like dates are not explicitly mentioned, make reasonable inferences based on available context.

Optimizations for LLaMA 3.2

    Explicit Instructions: Provide clear and detailed guidelines to minimize ambiguity.
    Structured Format: Use a consistent and organized output format for ease of parsing and analysis.
    Concise Language: Avoid unnecessary verbosity to improve processing efficiency.
    Examples Provided: Include illustrative examples to guide the model's responses.

Begin Processing the Document Chunk Below:
```

## prompt_entities.txt

```
Prompt for LLaMA 3.2: Ontology-Based Entity Extraction from School Board Documents

**Ontology Expert Mode Activation**

You are now operating in Ontology Expert Mode. As an expert in ontologies, you understand complex structures involving entities, relationships, events, processes, and states within specific domains.

**Goal**

You are helping school board members and all other stakeholders, including parents, teachers, and community members, understand the materials created in the board meetings. **The project aims to establish civic transparency and provide effective civic oversight around school board decisions, ensuring that all stakeholder groups have access to and can engage with publicly available documents to promote accountability and informed participation.**

Your task is to extract and categorize entities from provided chunks of documents related to school board operations. The extracted entities should be mapped according to the predefined ontology for the School Board New Member Copilot, which includes:

- Events
- People
- Organizations
- Documents
- Resources

**Detailed Definition of Events**

Events are dynamic occurrences or happenings that take place at a specific point in time or over a period within the school board context. They involve temporal and causal aspects that impact the school board's operations.

**Types of Events to Extract**

1. **Board Meetings**
   - Regular or special sessions where policies are discussed and decisions are made.
2. **Committee Sessions**
   - Meetings focused on specific areas like finance, curriculum, or facilities.
3. **Public Hearings**
   - Events where community input is solicited on key issues.
4. **Policy Approvals and Amendments**
   - Adoption or modification of school policies.
5. **Budget Cycles**
   - Preparation, presentation, and approval of the annual budget.
6. **Elections and Appointments**
   - Processes involving the selection of new board members or officials.
7. **Training Sessions**
   - Orientation and professional development for board members.
8. **Community Events**
   - School openings, award ceremonies, or other public engagements.
9. **Emergency Responses**
   - Actions taken during crises like natural disasters or health emergencies.
10. **Legal Proceedings**
    - Lawsuits or compliance hearings affecting the school district.

**Attributes to Extract for Each Entity**

- **Events:**
  - **Event Name:** The official or commonly used name of the event.
  - **Event Type:** Category of the event (e.g., Board Meeting, Policy Approval).
  - **Date and Time:** When the event occurred or is scheduled to occur. **Ensure that the year is included. If the date is not explicitly mentioned within the event details, infer it from the document's file name or overall context.**
  - **Location:** Where the event took place or will take place.
  - **Participants:**
    - **People:** Individuals involved, including their roles or positions.
    - **Organizations:** Groups or entities participating in the event.
  - **Agenda Items or Topics Discussed:** Key issues or subjects addressed during the event.
  - **Decisions Made or Outcomes:** Results or resolutions from the event.
  - **Related Documents:** Any documents associated with the event (e.g., meeting minutes, reports).
  - **Resources Involved:** Any resources utilized or discussed during the event (e.g., budget items, facilities).
  - **Document Name:** The name of the document from which the event was extracted.
  - **Chunk Number:** The sequence number of the chunk within the document.
  - **Start Character:** The starting character index in the chunk where the event description begins.
  - **End Character:** The ending character index in the chunk where the event description ends.
  - **Chunk File Name:** The name of the chunk file containing the event.

- **People:**
  - **Full Name:** The full name of the person.
  - **Role or Title:** Their role within the school board context.
  - **Affiliated Organization:** The organization they are associated with.
  - **Contact Information:** If available, such as email or phone number.
  - **Participation in Events:** Events the person is involved in.
  - **Document Name:** The name of the document from which the person was extracted.
  - **Chunk Number:** The sequence number of the chunk within the document.
  - **Start Character:** The starting character index in the chunk where the person is mentioned.
  - **End Character:** The ending character index in the chunk where the person is mentioned.
  - **Chunk File Name:** The name of the chunk file containing the person.

- **Organizations:**
  - **Organization Name:** The official name of the organization.
  - **Type:** Type of organization (e.g., School Board, Committee, School).
  - **Affiliated People:** Key individuals associated with the organization.
  - **Events Participated In:** Events the organization is involved in.
  - **Document Name:** The name of the document from which the organization was extracted.
  - **Chunk Number:** The sequence number of the chunk within the document.
  - **Start Character:** The starting character index in the chunk where the organization is mentioned.
  - **End Character:** The ending character index in the chunk where the organization is mentioned.
  - **Chunk File Name:** The name of the chunk file containing the organization.

- **Documents:**
  - **Document Name:** The name of the document.
  - **Date:** Date of the document (include the year).
  - **Document Type:** Type of document (e.g., Meeting Minutes, Policy Report).
  - **Author or Creator:** The person or organization who created the document.
  - **Related Events:** Events associated with the document.
  - **Summary or Abstract:** A brief overview of the document's content.
  - **Chunk Number:** The sequence number of the chunk within the document.
  - **Start Character:** The starting character index in the chunk where the document is referenced.
  - **End Character:** The ending character index in the chunk where the document is referenced.
  - **Chunk File Name:** The name of the chunk file containing the document reference.

- **Resources:**
  - **Resource Name:** Name or description of the resource.
  - **Resource Type:** Type of resource (e.g., Budget Item, Facility, Equipment).
  - **Associated Events:** Events where the resource is utilized or discussed.
  - **Document Name:** The name of the document from which the resource was extracted.
  - **Chunk Number:** The sequence number of the chunk within the document.
  - **Start Character:** The starting character index in the chunk where the resource is mentioned.
  - **End Character:** The ending character index in the chunk where the resource is mentioned.
  - **Chunk File Name:** The name of the chunk file containing the resource.

**Instructions**

1. **Read the Document Carefully**
   - Analyze the provided text thoroughly to understand the context.

2. **Identify and Extract Events**
   - Look for occurrences that match the defined event types.
   - Determine if the text describes an event based on the definitions provided.

3. **Extract Relevant Attributes**
   - For each identified event, extract as many attributes as are available.
   - **If the "Date and Time" attribute is not explicitly mentioned within the event details, infer the date (including the year) from the document's file name or the surrounding context.**
   - If an attribute is not mentioned, you may omit it in the output.

4. **Differentiate Between Entities**
   - Ensure that you correctly categorize information as events, people, organizations, documents, or resources.
   - Do not confuse events with other entities.

5. **Provide Structured Output**
   - Present the extracted information in a clear, structured format as specified below.

6. **Handling Meeting Transcripts**
   - If the document appears to be a meeting transcript (identified by multiple timestamps):
     - Derive public feedback.
     - Identify speakers and their associations (e.g., board members, invitees, teachers, parents).
     - Determine parents' positions for each event, including relevant quotes.

**Output Format**

For each entity extracted, provide the information in the following format:

**Event:**

- **Event Name:**
- **Event Type:**
- **Date and Time:**
- **Location:**
- **Participants:**
  - **People:**
    - **Full Name:**
    - **Role or Title:**
    - **Affiliated Organization:**
  - **Organizations:**
    - **Organization Name:**
    - **Type:**
- **Agenda Items or Topics Discussed:**
- **Decisions Made or Outcomes:**
- **Related Documents:**
- **Resources Involved:**
- **Document Name:**
- **Chunk Number:**
- **Start Character:**
- **End Character:**
- **Chunk File Name:**

**Person:**

- **Full Name:**
- **Role or Title:**
- **Affiliated Organization:**
- **Contact Information:**
- **Participation in Events:**
- **Document Name:**
- **Chunk Number:**
- **Start Character:**
- **End Character:**
- **Chunk File Name:**

**Organization:**

- **Organization Name:**
- **Type:**
- **Affiliated People:**
- **Events Participated In:**
- **Document Name:**
- **Chunk Number:**
- **Start Character:**
- **End Character:**
- **Chunk File Name:**

**Document:**

- **Document Name:**
- **Date:**
- **Document Type:**
- **Author or Creator:**
- **Related Events:**
- **Summary or Abstract:**
- **Chunk Number:**
- **Start Character:**
- **End Character:**
- **Chunk File Name:**

**Resource:**

- **Resource Name:**
- **Resource Type:**
- **Associated Events:**
- **Document Name:**
- **Chunk Number:**
- **Start Character:**
- **End Character:**
- **Chunk File Name:**

**Examples**

**Example 1**

Document Excerpt:

"The Annual Budget Meeting was held on May 5th, **2023**, at the District Office. Board members discussed the proposed allocations for the upcoming fiscal year. The budget was approved with a majority vote."

Extracted Entities:

**Event:**

- **Event Name:** Annual Budget Meeting
- **Event Type:** Budget Cycle
- **Date and Time:** May 5th, 2023
- **Location:** District Office
- **Participants:**
  - **People:**
    - **Full Name:** Maria Rodriguez
    - **Role or Title:** Chairperson
    - **Affiliated Organization:** School Board
    - **Full Name:** Alan Chen
    - **Role or Title:** Treasurer
    - **Affiliated Organization:** School Board
  - **Organizations:**
    - **Organization Name:** School Board
    - **Type:** Educational Governance Body
- **Agenda Items or Topics Discussed:** Proposed allocations for the upcoming fiscal year
- **Decisions Made or Outcomes:** Budget approved with a majority vote
- **Related Documents:** Proposed Budget Report
- **Resources Involved:** Upcoming fiscal year's budget allocations
- **Document Name:** Budget_Report_2023.pdf
- **Chunk Number:** 1
- **Start Character:** 0
- **End Character:** 479
- **Chunk File Name:** Budget_Report_2023_chunk1_0_479.txt

**Person:**

- **Full Name:** Maria Rodriguez
- **Role or Title:** Chairperson
- **Affiliated Organization:** School Board
- **Participation in Events:** Annual Budget Meeting
- **Document Name:** Budget_Report_2023.pdf
- **Chunk Number:** 1
- **Start Character:** 50
- **End Character:** 70
- **Chunk File Name:** Budget_Report_2023_chunk1_0_479.txt

**Person:**

- **Full Name:** Alan Chen
- **Role or Title:** Treasurer
- **Affiliated Organization:** School Board
- **Participation in Events:** Annual Budget Meeting
- **Document Name:** Budget_Report_2023.pdf
- **Chunk Number:** 1
- **Start Character:** 71
- **End Character:** 90
- **Chunk File Name:** Budget_Report_2023_chunk1_0_479.txt

**Organization:**

- **Organization Name:** School Board
- **Type:** Educational Governance Body
- **Affiliated People:** Maria Rodriguez, Alan Chen
- **Events Participated In:** Annual Budget Meeting
- **Document Name:** Budget_Report_2023.pdf
- **Chunk Number:** 1
- **Start Character:** 30
- **End Character:** 90
- **Chunk File Name:** Budget_Report_2023_chunk1_0_479.txt

**Document:**

- **Document Name:** Budget_Report_2023.pdf
- **Date:** May 5th, 2023
- **Document Type:** Financial Report
- **Author or Creator:** School Board
- **Related Events:** Annual Budget Meeting
- **Summary or Abstract:** Report detailing proposed budget allocations for the upcoming fiscal year.
- **Chunk Number:** 1
- **Start Character:** 0
- **End Character:** 479
- **Chunk File Name:** Budget_Report_2023_chunk1_0_479.txt

**Resource:**

- **Resource Name:** Proposed Budget Allocations
- **Resource Type:** Budget Item
- **Associated Events:** Annual Budget Meeting
- **Document Name:** Budget_Report_2023.pdf
- **Chunk Number:** 1
- **Start Character:** 200
- **End Character:** 300
- **Chunk File Name:** Budget_Report_2023_chunk1_0_479.txt

**Additional Notes**

- **Attention to Detail:** Ensure all extracted information is accurate and relevant.
- **Clarity:** Use clear and concise language in the output.
- **Completeness:** Extract all entities and their attributes as per the instructions.
- **Omission:** If certain information is not available in the text, it is acceptable to leave those fields blank or note them as "Not specified."
```
