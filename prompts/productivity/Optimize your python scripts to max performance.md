---
title: Nd Review The Optimized Version With Clear Annotations
category: productivity
type: workflow
tags:
- workflow
- organization
- python
- review
- explanation
favorite: false
created: '2025-06-05'
use_count: 0
auto_categorized: '2025-06-05 19:19:36'
categorization_confidence: 0.9
last_used: null
---

Ever spent hours trying to speed up your Python code only to find that your performance tweaks don't seem to hit the mark? If you’re a Python developer struggling to pinpoint and resolve those pesky performance bottlenecks in your code, then this prompt chain might be just what you need.

This chain is designed to guide you through a step-by-step performance analysis and optimization workflow for your Python scripts. Instead of manually sifting through your code looking for inefficiencies, this chain breaks the process down into manageable steps—helping you format your code, identify bottlenecks, propose optimization strategies, and finally generate and review the optimized version with clear annotations.

How This Prompt Chain Works
This chain is designed to help Python developers improve their code's performance through a structured analysis and optimization process:

Initial Script Submission: Start by inserting your complete Python script into the [SCRIPT] variable. This step ensures your code is formatted correctly and includes necessary context or comments.

Identify Performance Bottlenecks: Analyze your script to find issues such as nested loops, redundant calculations, or inefficient data structures. The chain guides you to document these issues with detailed explanations.

Propose Optimization Strategies: For every identified bottleneck, the chain instructs you to propose targeted strategies to optimize your code (like algorithm improvements, memory usage enhancements, and more).

Generate Optimized Code: With your proposed improvements, update your code, ensuring each change is clearly annotated to explain the optimization benefits, such as reduced time complexity or better memory management.

Final Review and Refinement: Finally, conduct a comprehensive review of the optimized code to confirm that all performance issues have been resolved, and summarize your findings with actionable insights.

```text
The Prompt Chain
You are a Python Performance Optimization Specialist. Your task is to provide a Python code snippet that you want to improve. Please follow these steps:

1. Clearly format your code snippet using proper Python syntax and indentation.
2. Include any relevant comments or explanations within the code to help identify areas for optimization.

Output the code snippet in a single, well-formatted block.

Step 1: Initial Script Submission
You are a Python developer contributing to a performance optimization workflow. Your task is to provide your complete Python script by inserting your code into the [SCRIPT] variable. Please ensure that:

1. Your code is properly formatted with correct Python syntax and indentation.
2. Any necessary context, comments, or explanations about the application and its functionality are included to help identify areas for optimization.

Submit your script as a single, clearly formatted block. This will serve as the basis for further analysis in the optimization process.
~
Step 2: Identify Performance Bottlenecks
You are a Python Performance Optimization Specialist. Your objective is to thoroughly analyze the provided Python script for any performance issues. In this phase, please perform a systematic review to identify and list any potential bottlenecks or inefficiencies within the code. Follow these steps:

1. Examine the code for nested loops, identifying any that could be impacting performance.
2. Detect redundant or unnecessary calculations that might slow the program down.
3. Assess the use of data structures and propose more efficient alternatives if applicable.
4. Identify any other inefficient code patterns or constructs and explain why they might cause performance issues.

For each identified bottleneck, provide a step-by-step explanation, including reference to specific parts of the code where possible. This detailed analysis will assist in subsequent optimization efforts.
~
Step 3: Propose Optimization Strategies
You are a Python Performance Optimization Specialist. Building on the performance bottlenecks identified in the previous step, your task is to propose targeted optimization strategies to address these issues. Please follow these guidelines:

1. Review the identified bottlenecks carefully and consider the context of the code.
2. For each bottleneck, propose one or more specific optimization strategies. Your proposals can include, but are not limited to:
   - Algorithm improvements (e.g., using more efficient sorting or searching methods).
   - Memory usage enhancements (e.g., employing generators, reducing unnecessary data duplication).
   - Leveraging efficient built-in Python libraries or functionalities.
   - Refactoring code structure to minimize nested loops, redundant computations, or other inefficiencies.
3. For every proposed strategy, provide a clear explanation of how it addresses the particular bottleneck, including any potential trade-offs or improvements in performance.
4. Present your strategies in a well-organized, bullet-point or numbered list format to ensure clarity.

Output your optimization proposals in a single, clearly structured response.
~
Step 4: Generate Optimized Code
You are a Python Performance Optimization Specialist. Building on the analysis and strategies developed in the previous steps, your task now is to generate an updated version of the provided Python script that incorporates the proposed optimizations. Please follow these guidelines:

1. Update the Code:
   - Modify the original code by implementing the identified optimizations.
   - Ensure the updated code maintains proper Python syntax, formatting, and indentation.

2. Annotate Your Changes:
   - Add clear, inline comments next to each change, explaining what optimization was implemented.
   - Describe how the change improves performance (e.g., reduced time complexity, better memory utilization, elimination of redundant operations) and mention any trade-offs if applicable.

3. Formatting Requirements:
   - Output the entire optimized script as a single, well-formatted code block.
   - Keep your comments concise and informative to facilitate easy review.

Provide your final annotated, optimized Python code below:
~
Step 5: Final Review and Refinement
You are a Python Performance Optimization Specialist. In this final stage, your task is to conduct a comprehensive review of the optimized code to confirm that all performance and efficiency goals have been achieved. Follow these detailed steps:

1. Comprehensive Code Evaluation:
   - Verify that every performance bottleneck identified earlier has been addressed.
   - Assess whether the optimizations have resulted in tangible improvements in speed, memory usage, and overall efficiency.

2. Code Integrity and Functionality Check:
   - Ensure that the refactored code maintains its original functionality and correctness.
   - Confirm that all changes are well-documented with clear, concise comments explaining the improvements made.

3. Identify Further Opportunities for Improvement:
   - Determine if there are any areas where additional optimizations or refinements could further enhance performance.
   - Provide specific feedback or suggestions for any potential improvements.

4. Summarize Your Findings:
   - Compile a structured summary of your review, highlighting key observations, confirmed optimizations, and any areas that may need further attention.

Output your final review in a clear, organized format, ensuring that your feedback is actionable and directly related to enhancing code performance and efficiency.
Understanding the Variables
```

Example Use Cases
As a Python developer, you can use this chain to systematically optimize and refactor a legacy codebase that's been slowing down your application.

Use it in a code review session to highlight inefficiencies and discuss improvements with your development team.

Apply it in educational settings to teach performance optimization techniques by breaking down complex scripts into digestible analysis steps.

Pro Tips
Customize each step with your parameters or adapt the analysis depth based on your code’s complexity.

Use the chain as a checklist to ensure every optimization aspect is covered before finalizing your improvements.

Want to automate this entire process? Check out [Agentic Workers] - it'll run this chain autonomously with just one click. The tildes (~) are meant to separate each prompt in the chain. Agentic Workers will automatically fill in the variables and run the prompts in sequence. (Note: You can still use this prompt chain manually with any AI model!)

Happy prompting and let me know what other prompt chains you want to see! 🤖