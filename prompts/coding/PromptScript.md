---
title: '# Promptscript'
category: coding
type: template
tags:
- programming
- development
- article
- comparison
- research
variables:
- ' '
- 'age: 30, interests: "technology, photography"'
- books
- color:user_response
- common_issues
- 'expertise: "highly skilled"'
- guide
- 'question:f"@user: What is your favorite color?"'
- 'task: "Imagine and describe a disruptive new state-of-the-art model architecture"'
- 'text: "Article about renewable energy"'
- 'topic1: "electric cars", topic2: "gasoline cars"'
- 'topic: "AI ethics"'
- 'topic: "quantum computing"'
- 'topic: "setting up a home network"'
favorite: false
created: '2025-06-05'
use_count: 0
auto_categorized: '2025-06-05 19:21:03'
categorization_confidence: 0.9
last_used: null
---

# PromptScript

```markdown
Symbols and Conventions:

1. [ ]: Define tasks using square brackets.
   Example: [research], [summarize], [suggest]

2. { }: Specify input parameters for tasks using curly braces.
   Example: [research]{topic}}}}: "quantum computing"}

3. ( ): Set context or provide additional information using parentheses.
   Example: [suggest](gifts){age}: 30, interests: "technology, photography"}

4. < >: Define the expected output format using angle brackets.
   Example: [summarize]<bullet_points>{text}: "Article about renewable energy"}

5. | : Separate multiple tasks or options using the pipe symbol.
   Example: [research]{topic}: "quantum computing"} | [suggest]{books}

6. @ : Tag a user or AI for multi-turn conversations.
   Example: @user: What is your favorite color? | @AI: My favorite color is blue.

7. -> : Indicate a sequence of tasks or actions using the arrow symbol.
   Example: [research]{topic}: "AI ethics"}->[summarize]<paragraph>

8. [[ ]]: Indicate a loop or repetition using double brackets.
   Example: [[suggest](gifts){age: 30, interests: "technology, photography"}]]*
   
   1. Research and summarize an article on AI ethics in a paragraph format, then suggest books on the same topic:
   [research]{topic}: "AI ethics"}->[[summarize]<paragraph> | [suggest](books)[topic]]

2. Ask the user for their favorite color and then suggest matching clothing items:
  [wait](user_response){question}:f"@user: What is your favorite color?"} | @AI: [[suggest](clothing){color}:user_response}]]*3

3. Provide a step-by-step guide to setting up a home network and troubleshoot common issues in a bullet points list:
   [guide](technology){topic}: "setting up a home network"}->[[summarize]{guide} | [troubleshoot]<bullet_points>{common_issues}]

4. Compare two topics and provide a list of pros and cons:
   [compare]{topic}1}: "electric cars", topic2: "gasoline cars"}->[evaluate]<pros_and_cons>

5. AI will become an AI scientist, and try to develop a new state-of-the-art AI model architecture:
   [become](AI_scientist){expertise}: "highly skilled"}->[assist]{task}: "Imagine and describe a disruptive new state-of-the-art model architecture"}
```