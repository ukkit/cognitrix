---
title: 'Follow The Instructions Below:'
category: productivity
type: workflow
tags:
- workflow
- organization
- explanation
- reporting
- planning
favorite: false
created: '2025-06-05'
use_count: 0
auto_categorized: '2025-06-05 19:19:36'
categorization_confidence: 0.9
last_used: null
---

Ever felt overwhelmed trying to complete a comprehensive brand audit for your business?

This prompt chain is designed to guide you through the entire process of developing your brand identity and conducting a full digital audit. It breaks down a complex task into manageable steps, making it easier to focus on one part at a time, while ultimately producing a thorough and structured evaluation of your brand’s online presence.

How This Prompt Chain Works
This chain is designed to assist you in building a brand strategy and performing a detailed digital audit. It spans from establishing your brand name to finalizing a comprehensive report and strategic recommendations. Here's how it works:

The first prompt focuses on your brand identity by asking you to specify your brand name following a strict format. This ensures consistency in subsequent steps.

The next prompt shifts to a digital audit where you list out all the platforms your brand is active on, using bullet points for clarity.

Each subsequent prompt builds upon insights gathered previously – from evaluating website performance to analyzing social media engagement.

Repetitive tasks, such as listing platforms or rating performance, are streamlined with detailed instructions, saving you time and reducing errors.

Variables like BRAND NAME are placeholders meant for you to replace with your actual brand name, ensuring personalization and accuracy. The tilde (~) symbol is used to separate each individual step in the chain.

The Prompt Chain

```text
You are a brand strategist tasked with defining the identity of your business. Your first step is to provide your brand name in a designated format. Please follow the instructions below:

1. Replace [BRAND NAME] with the actual name of your brand.
2. Use the exact format as shown: BRAND NAME = [BRAND NAME].
3. Ensure that your submission has no additional characters or spaces beyond the specified format.

Once you have inserted your brand name accordingly, proceed to the next step in the workflow.
~
You are a digital audit specialist tasked with evaluating your brand’s online presence. In this step, you will define the scope of your audit by identifying all primary web platforms and social media channels that feature your brand. Using the brand name you provided in the first step, please follow these instructions:

1. List each platform where your brand is active. This must include your website, Facebook page, Instagram account, Twitter profile, LinkedIn presence, and any other relevant channels.
2. Present your answer as a bullet list with one platform per bullet.
3. Ensure clarity and conciseness, avoiding additional commentary.

Example output:
• Website
• Facebook
• Instagram
• Twitter
• LinkedIn
~
You are a digital audit specialist tasked with evaluating the online performance of your brand's website. In this step, your objective is to assess key aspects of the website where [BRAND NAME] is featured. Please follow the instructions below:

1. Evaluate the website based on the following criteria:
   • Loading Speed
   • User Experience
   • Design
   • Content Quality
2. For each criterion, assign a rating from 1 (poor) to 10 (excellent).
3. Provide a concise rationale (2-3 sentences) justifying each rating.

Instructions for submission:
• Present your findings in a clear, structured format (e.g., bullet points or numbered list).
• Ensure each criterion is followed by its corresponding rating and rationale.

Example format:
• Loading Speed: 7 – The website loads moderately fast but could benefit from further optimization.
• User Experience: 8 – The navigation is intuitive and user-friendly.
• Design: 6 – The visual design is adequate but lacks modern appeal.
• Content Quality: 9 – The content is informative and engaging, with minor areas for improvement.

Once complete, please proceed with your evaluation using the structure provided above.
~
You are a digital audit specialist tasked with evaluating the social media performance for your brand [BRAND NAME]. In this step, review the engagement metrics from each social media platform you previously identified. Please follow these instructions:

1. For each platform, gather and summarize the following metrics:
   • Number of Followers
   • Average Likes per Post
   • Average Shares per Post
   • Average Comments per Post
   • Engagement Rate

2. Based on the collected data, assign an overall effectiveness rating to each platform on a scale of 1 (poor) to 10 (excellent).

3. Structure your submission as follows:
   • List each platform in a bullet point and under it, provide the metric breakdown and your effectiveness rating along with a brief evaluation (2-3 sentences) explaining your rationale.

Example format:
• Facebook:
   - Followers: 10,000
   - Average Likes/Post: 150
   - Average Shares/Post: 20
   - Average Comments/Post: 15
   - Engagement Rate: 3.5%
   - Effectiveness Rating: 8 – Facebook shows robust engagement, although content variety could be enhanced.

Ensure your submission is clear, concise, and formatted as instructed. Once complete, proceed to the next step.
~
You are a digital audit specialist tasked with synthesizing the positive aspects of your brand's online presence based on the analysis conducted in previous steps. In this step, your objective is to identify and articulate at least three strengths of [BRAND NAME]'s online presence. Please follow the instructions below:

1. List at least three specific strengths, each representing a key positive aspect identified through your previous analysis.
2. Under each point, provide a brief explanation (2-3 sentences) detailing why this aspect is considered a strength.
3. Use a clear, structured bullet point format for your submission.

Example output:
• Strong Website Performance: The website demonstrates fast loading times and user-friendly navigation, contributing to a positive user experience.
• High Social Media Engagement: The brand consistently achieves strong engagement metrics across social platforms, highlighting effective audience interaction.
• Quality Content Strategy: The content is well-curated, engaging, and aligns with the brand’s messaging, fostering customer trust.

Ensure your submission is concise and follows the provided format. Once completed, proceed to the next step.
~
You are a digital audit specialist tasked with identifying improvements in your brand's online presence. In this step, your goal is to pinpoint and elaborate on at least three weaknesses based on the analysis you previously conducted. Please adhere to the following instructions:

1. List a minimum of three specific weaknesses observed in [BRAND NAME]'s online presence.
2. For each identified weakness, provide a concise explanation (2-3 sentences) detailing why it is considered a weakness.
3. Format your response as a bullet-point list, ensuring clarity and structure.

Example:
• Weak Content Engagement: The content shows low interaction across key platforms, limiting audience reach and engagement.
• Outdated Website Design: The website design fails to meet modern usability standards, affecting user trust and retention.
• Poor Mobile Optimization: The mobile experience is suboptimal due to slow load times and an unresponsive layout.

Ensure your submission focuses solely on the identified weaknesses and their impacts. Once you have completed this step, proceed to the next stage of the analysis.
~
You are a digital audit specialist focused on enhancing your brand's online performance. Building on the previously identified weaknesses, your task is to propose targeted opportunities for improvement. Please follow these instructions:

1. Review the identified weaknesses from your earlier analysis.
2. List at least three specific opportunities or strategies that can address these weaknesses and elevate [BRAND NAME]'s online presence and engagement.
3. For each opportunity, provide a concise explanation (2-3 sentences) describing how it can remediate the identified issues and boost performance.
4. Use a clear bullet-point format for your submission, ensuring each opportunity is distinct.

Example format:
– Brief explanation of how this strategy will improve a specific weakness.
– Brief explanation of how this strategy will enhance online engagement.
 – Brief explanation of how this strategy addresses a key identified weakness.

Ensure your response is structured, precise, and directly linked to the weaknesses outlined earlier. Once completed, please proceed to the next step in the workflow.
~
You are a digital strategist tasked with elevating [BRAND NAME]'s online presence. Using insights from your previous analysis, your objective is to develop a strategic action plan with clear, actionable steps for enhancing both its website and social media channels. Please adhere to the following instructions:

1. Identify and list the specific actions necessary to improve [BRAND NAME]'s web and social media performance.
2. For each action, include the following details:
   - A brief description of the step.
   - A defined timeline or deadline for implementation.
   - The responsible party or team designated to execute the step.
3. Present your action plan in a structured format (e.g., bullet points or numbered list) with each action clearly detailed.
4. Ensure that each step is directly linked to the identified opportunities or weaknesses from your prior analysis.

Example Format:
• Action Step: Update website design for better user experience.
   - Timeline: Complete within 3 months.
   - Responsible Party: Web Design Team.
• Action Step: Boost social media engagement through targeted campaigns.
   - Timeline: Launch within 1 month with weekly performance reviews.
   - Responsible Party: Social Media Manager.
• Action Step: Implement on-page SEO improvements.
   - Timeline: Roll out over 6 weeks.
   - Responsible Party: SEO Specialist.

Once your plan is finalized, review it to ensure clarity, feasibility, and alignment with your overall strategy for [BRAND NAME].
~
You are a digital strategist tasked with conducting a competitor analysis for your brand. In this step, you will identify and evaluate 2 to 3 competitors to uncover best practices and areas for improvement that [BRAND NAME] can adopt.

Please follow these instructions:
1. Competitor Identification:
   • Select 2-3 direct competitors of [BRAND NAME].
   • Ensure that these competitors have an active presence both on the web and social media.

2. Analysis of Competitors:
   For each competitor, provide an analysis that includes:
   • Web Presence: Evaluate aspects such as website design, content quality, user experience, and responsiveness.
   • Social Media Presence: Assess engagement metrics, content strategy, follower interaction, and overall effectiveness.
   • Strengths: List specific areas where the competitor excels.
   • Opportunities for [BRAND NAME]: Highlight areas where [BRAND NAME] can improve by learning from these competitors.

3. Submission Format:
   • Present your findings in a structured format, such as a bullet-point list or a numbered list.
   • Clearly label each competitor and under each, provide the detailed analysis as outlined above.

Example Format:
• Competitor A:
   - Web Presence:
   - Social Media Presence:
   - Strengths:
   - Opportunities for [BRAND NAME]

Once your competitor analysis is complete, proceed to the next step in your workflow.
~
You are a digital audit specialist tasked with finalizing your audit for [BRAND NAME]. In this final step, you will compile a comprehensive report that summarizes the entire audit process. Please follow the instructions below:

1. Overall Summary: Begin with an executive summary that encapsulates the key insights from the audit process.

2. Structured Sections: Organize your report using the following clear headings and include the corresponding details under each section:
   • Strengths: List at least three major strengths identified in [BRAND NAME]’s online presence along with brief 2-3 sentence explanations for each.
   • Weaknesses: List at least three weaknesses along with concise explanations detailing their impact.
   • Opportunities: Highlight at least three actionable opportunities for enhancing the brand’s digital performance with brief rationales.
   • Strategic Action Plan: Summarize the proposed strategies including key steps, timelines, and responsible parties as outlined in your previous analysis.

3. Formatting Requirements:
   • Use clear headings for each section.
   • Present bullet-pointed lists where applicable.
   • Maintain clarity, conciseness, and a professional tone throughout the report.

Once finished, review the report to ensure it accurately reflects the insights gathered during the audit and provides a cohesive direction for future improvements.
~
You are a digital strategist finalizing your comprehensive audit for [BRAND NAME]. Based on the detailed analysis conducted in previous steps, your task is to provide 3 high-level recommendations to optimize the overall brand strategy. Please follow these instructions:

1. List exactly 3 recommendations. Each recommendation should focus on a major strategic initiative that leverages insights from your audit.
2. For each recommendation, include the following details:
   - Recommendation Title: A concise title that summarizes the initiative.
   - Brief Description: 2-3 sentences explaining the rationale and potential impact of the recommendation.
3. Present your recommendations in a clear, bulleted list.
4. Ensure that your submission is clear, concise, and directly aligned with the audit insights provided in the previous steps.

Example Format:
• Recommendation 1:
   - Description: Brief explanation of the recommendation, highlighting how it addresses key audit findings and can optimize the brand strategy.
• Recommendation 2:
   - Description: Brief explanation of the recommendation, highlighting how it addresses key audit findings and can optimize the brand strategy.
• Recommendation 3:
   - Description: Brief explanation of the recommendation, highlighting how it addresses key audit findings and can optimize the brand strategy.

Once you have provided your recommendations, please review them to ensure alignment with the overall audit findings and the strategic vision for [BRAND NAME].
~
You are a digital audit specialist responsible for ensuring the quality and effectiveness of [BRAND NAME]'s audit report. In this final review step, your objective is to comprehensively reassess the entire audit process and the finalized report. Please follow these instructions:

1. Reevaluate the Audit Report:
   - Read through the entire audit report, including the executive summary, analysis sections (strengths, weaknesses, opportunities), and the strategic action plan.
   - Check for clarity and coherence in presenting the information.
   - Confirm that all sections are logically connected and that key insights are clearly articulated.

2. Refine for Actionability:
   - Ensure that the report provides actionable insights that can directly inform strategic decisions.
   - Verify that the strategic action plan is fully aligned with the audit findings and recommendations.

3. Provide your Feedback:
   - Identify any areas that require further clarification or restructuring.
   - Suggest improvements to enhance the report's usability and impact, if necessary.

Formatting Requirements:
   - Use bullet points to list any identified issues and recommended refinements.
   - Maintain a professional tone and clear, concise language.

Once your review is complete, update the report to reflect these refinements and finalize it for implementation.
Understanding the Variables
```

Example Use Cases
A startup defining its brand identity and wanting a structured launch plan.

A marketing agency conducting an audit for a client and needing a detailed, replicable process.

A business owner looking to understand and improve their digital presence step-by-step.

Pro Tips
Customize each step by adding more specific instructions or criteria based on your unique brand needs.

Keep your responses concise and follow the exact formatting to ensure smooth automated processing with Agentic Workers.

Want to automate this entire process? Check out Agentic Workers - it'll run this chain autonomously with just one click. The tildes (~) are meant to separate each prompt in the chain. Agentic workers will automatically fill in the variables and run the prompts in sequence. (Note: You can still use this prompt chain manually with any AI model!)

Happy prompting and let me know what other prompt chains you want to see! 🚀