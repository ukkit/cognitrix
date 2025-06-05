---
title: '# How To Write Good Prompts For Generating Code From Llms'
category: technical
type: workflow
tags:
- documentation
- systems
- python
- sql
- api
favorite: false
created: '2025-06-05'
use_count: 0
auto_categorized: '2025-06-05 19:19:36'
categorization_confidence: 0.9
last_used: null
---

# How to write good prompts for generating code from LLMs

Large Language Models (LLMs) have revolutionized code generation, but to get high-quality, useful output, creating effective prompts is crucial. The quality of the generated code is heavily dependent on the quality of the prompts provided. A poorly framed prompt can lead to incomplete, incorrect, or generic responses, whereas a well-structured prompt maximizes the model’s potential. In this article, we will explore advanced strategies for writing effective prompts to generate high-quality code with LLMs.

## Provide Detailed Context

When interacting with LLMs for code generation, the depth and quality of context provided directly correlates with the relevance and accuracy of the output.

Key elements to include:

- Specific problem domain
- Existing codebase characteristics
- Implementation constraints
- Performance requirements
- Architectural patterns already in use

Additionally, you can use @references to point the model to specific files or functions, making your request more precise. Instead of describing a function in text, you can directly reference it.

```text
❌ Poor: "Create a user authentication system."

✅ Better: "Create a JWT-based authentication system for a Node.js Express API that integrates with our MongoDB user collection. The system should handle password hashing with bcrypt, issue tokens valid for 24 hours, and implement refresh token rotation for security. Our existing middleware pattern uses async/await syntax. Refer to @authMiddleware.js for the middleware structure and @userModel.js for the user schema."
```

By using @authMiddleware.js and @userModel.js, you ensure the generated code aligns with your existing setup, reducing integration issues and manual adjustments.

## Break Down Problems Into Steps

Complex coding tasks require systematic decomposition into manageable units. This approach begins with:

- Start with clear functionality requirements
- Analyze directory structure and code organization
- Guide the LLM through logical implementation steps for the desired functionality while respecting established architectural boundaries and design patterns.

For instance, when implementing a data processing pipeline, first clarify the input data structure, transformation logic, error handling requirements, and expected output format. Next, analyze the directory structure and determine where the new functionality should be implemented.

Consider factors such as dependency relationships, module boundaries, and code organization principles. This step ensures that generated code will integrate seamlessly with the existing codebase.

## Choose the Correct Model for the Job

Different LLMs exhibit varying strengths in code generation tasks. One model may excel at understanding complex requirements and generating code with strong logical consistency, while another model may offer advantages in certain programming languages or frameworks. When evaluating which LLM to use, key technical factors to consider:

- Context window capacity (essential when working with extensive codebases)
- Language/framework proficiency
- Domain-specific knowledge
- Consistency across iterations
- Example comparison:

| Task | Model Selection Consideration |
| Complex enterprise architecture | Models with larger context windows excel at maintaining consistency across large codebases |
| ML pipeline implementation | Models with stronger mathematics and data science training perform better |
| Frontend component generation | Models with recent training on modern frameworks provide up-to-date patterns |

## Be Specific When Referring to Existing Patterns

Specificity in prompts significantly improves code quality by eliminating uncertainity. Technical specificity involves explicit references to existing implementation patterns. Rather than requesting generic implementations, point to specific reference points in the codebase. For example:

```text
❌ Poor: "Write a function to process user data."

✅ Better: "Create a new method in the UserProcessor class (src/services/UserProcessor.js) that transforms user data following the same functional approach used in the transformPaymentData method. Prioritize readability over performance as this runs asynchronously."
```

This approach extends to naming conventions, coding standards, and architectural patterns. Specify whether the code should follow functional or object-oriented methodologies, indicate preferred design patterns, and clarify whether performance or readability should be prioritized.

## Regenerate Rather Than Rollback

When encountering issues with generated code, complete regeneration of the problematic parts often gives us much better results compared to incremental fixes. This method originates from how LLMs interpret context and produce responses.

Why regeneration works better?

- Provides fresh perspective without previous errors
- Avoids propagating flawed logic
- Allows incorporation of new constraints

This technique is particularly effective for algorithmic challenges or complex logic implementations where small errors can propagate throughout the solution, making isolated fixes problematic.

Example:

```text
"Let's try a different approach for the sorting algorithm. The previous implementation had O(n²) complexity, which won't work for our dataset size. Please regenerate the solution focusing on an O(n log n) approach using a merge sort pattern similar to what we use in our other data processing functions."
```

## Implement Reflection Through Multiple Approaches

Leveraging LLMs' ability to generate multiple solution approaches enhances code quality through comparative analysis. Begin by requesting the model to generate two or three distinct implementation strategies, each with its own strengths and weaknesses.

Once multiple approaches are generated, prompt the LLM to analyze the trade-offs between them considering factors such as time complexity, space efficiency, readability, and maintainability. This reflection process enables the model to select and refine the most appropriate solution based on the specific requirements.

Example:

```text
"Generate three different approaches to implement a caching system for our API responses:

1. An in-memory LRU cache using a custom data structure
2. A Redis-based distributed cache solution
3. A file-system based approach with TTL

For each approach, analyze time complexity, memory usage, scalability across multiple servers, and implementation complexity."
```

## Implement Self-Review Mechanisms

Self-review prompting enhances code quality by guiding the LLM through a systematic evaluation of its output. Implement this by explicitly requesting the model to cross-check its generated code after completion. The review should assess aspects such as:

- Correctness (logical errors)
- Efficiency (performance issues)
- Edge case handling
- Security vulnerabilities
- Adherence to requirements

During self-review, the model can identify potential issues such as race conditions in concurrent code, memory leaks in resource management, or vulnerability points in security-critical sections. Once issues are identified, the model can immediately refine the implementation to address these concerns. This approach mirrors established software engineering practices like code review and static analysis, but performs them within the same prompt-response cycle, significantly improving the initial code quality.

## Give the Model a Persona or Frame of Reference

Assigning a technical persona to the LLM establishes a consistent perspective for code generation. When prompted to adopt the mindset of a senior backend engineer with expertise in distributed systems, the model will prioritize scalability, fault tolerance, and performance considerations in its generated code. Similarly, a security-focused persona will emphasize input validation, proper authentication flows, and potential vulnerability mitigation.

The technical frame of reference should match the requirements of the task.

Effective personas by task:

- Backend systems: "Senior backend engineer with distributed systems expertise"
- Security features: "Security architect with OWASP expertise"
- Infrastructure: "DevOps engineer focusing on cloud-native solutions"
- Frontend: "UX-focused frontend developer with accessibility expertise"

This technique leverages the model's ability to imitate domain expertise, resulting in code that better reflects established practices within specific technical domains.

Example:

```text
"Act as a senior security engineer conducting a code review. Create a user registration system in Python/Django that implements proper password handling, input validation, and protection against common web vulnerabilities."
```

## Clarify Language, Framework, or Library Constraints

Explicit specification of technical constraints ensures compatibility with the target environment. Begin by clearly stating the programming language version (e.g., Python 3.9, TypeScript 4.5) to ensure language features used in the generated code are available in the production environment. Similarly, specify framework versions and their specific conventions, such as "FastAPI 0.95 with Pydantic v2 for data validation."

Additionally, provide information about library dependencies and their integration points. For instance, when requesting database interaction code, specify whether to use an ORM like SQLAlchemy or raw SQL queries, and clarify connection handling expectations. This level of specificity prevents the generation of code that relies on unavailable dependencies or incompatible versions.

Example:

```text
"Generate a REST API endpoint using:

- Python 3.9
- FastAPI 0.95 with Pydantic v2 models
- SQLAlchemy 2.0 for database queries
- JWT authentication using our existing AuthManager from auth_utils.py
- Must be compatible with our PostgreSQL 13 database"
```

## Implement Chain of Thought Prompting

Chain of thought prompting enhances code generation by guiding the LLM through a logical progression of reasoning steps. This technique involves instructing the model to decompose complex problems into sequential reasoning stages before writing code.

Sequential reasoning stages to request:

- Initial explanation of the conceptual approach
- Pseudocode outline of the solution
- Implementation details for each component
- Complete integrated implementation

Chain of thought prompting is effective for algorithms with complex logic or data transformations. It reduces logical errors, improves coherence, and offers visibility into the model's reasoning, allowing for corrections before the final code is produced.

Unlike the "break down into steps" approach, which focuses on task decomposition, chain of thought prompting emphasizes making the model's reasoning explicit, helping ensure the logic is sound before accepting the final solution.

## Tailor Prompts to the Model's Unique Strengths

Different LLMs exhibit varying capabilities that can be leveraged through specialized prompting strategies.

Adaptation strategies:

- For limited context windows: Focus on algorithmic guidance
- For strong functional programming models: Frame problems using functional patterns
- For models with framework expertise: Leverage specific framework terminology

Understanding a model's training biases also informs effective prompting. Some models may excel at particular programming paradigms or languages based on their training data distribution. For instance, a model with strong representation of functional programming concepts in its training data will respond better to prompts framed in functional terms for appropriate problems.

## Specify Edge Cases and Constraints

Comprehensive edge case consideration significantly improves code robustness. Technical edge cases vary by domain but commonly include boundary values, resource limitations, and exceptional conditions. When requesting implementations, clearly list these factors, for instance, specifying how a data processing function should handle empty inputs, malformed data, or values exceeding expected ranges.

By considering these constraints upfront, the generated code can incorporate appropriate validation logic, error handling mechanisms, and performance optimizations tailored to the specified limitations.

Example:

```text
"Implement a file processing function that handles:

- Empty files (return empty result)
- Files exceeding 1GB (process in chunks)
- Malformed CSV data (log error, continue processing valid rows)
- Concurrent access (implement appropriate locking)
- Network interruptions (implement resume capability)"
```

Mastering prompt engineering for code generation is both an art and a science that dramatically improves development efficiency. By implementing these strategic approaches, developers can transform LLMs from basic code generators into sophisticated development partners, enabling the creation of more robust, efficient, and maintainable software solutions.