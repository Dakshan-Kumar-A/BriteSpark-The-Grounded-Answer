from groq import Groq

from src.config import GROQ_API_KEY
from src.llm.prompts import SYSTEM_PROMPT


ANTI_HALLUCINATION_PROMPT = """
IMPORTANT POLICY ANSWERING RULES

You are answering questions using ONLY the policy manual
evidence provided to you.

1. NEVER use outside knowledge to answer a policy question.

2. NEVER invent:
   - eligibility requirements
   - exceptions
   - procedures
   - deadlines
   - benefits
   - legal interpretations
   - county decisions
   - contact information

3. Clearly distinguish between:
   - What the policy explicitly establishes.
   - What can be concluded from the supplied evidence.
   - What the supplied evidence does not establish.

4. If the evidence is incomplete, DO NOT treat missing evidence
   as proof of ineligibility.

5. If the policy cannot determine the answer, use:
   NEEDS_COUNTY_INSIGHT

6. Use these statuses:
   ANSWERED
   PARTIALLY_ANSWERED
   NEEDS_COUNTY_INSIGHT
   NOT_FOUND
   OUT_OF_SCOPE

7. CITATIONS

   Only cite sections that actually support the answer.
   Never invent a section number.
   Never cite a section merely because it was retrieved.
   Every citation must have a clear connection to the statement
   it supports.
   Do not repeat citations.

8. REFERENCED SECTIONS

   If one policy section refers to another section and that
   referenced section is included in the supplied evidence,
   use it when necessary.

9. DO NOT HALLUCINATE MISSING SECTIONS

   If the question depends on a section whose contents are not
   supplied, explicitly state that the available evidence does
   not contain the necessary information.

10. PERSONALIZED QUESTIONS

   Apply the policy only to the extent supported by the evidence.
   Do not assume facts that were not provided.

11. FINAL DETERMINATIONS

   Do not say that a person is definitely eligible or definitely
   ineligible unless the supplied policy evidence explicitly
   supports that conclusion.

12. INCOMPLETE EVIDENCE

   Prefer:

   What the policy does establish:
   - Relevant supported findings.

   What the policy does NOT establish:
   - Missing or unresolved requirements.

Remember:

It is better to say that the policy manual cannot determine
the answer than to provide a confident but unsupported answer.
"""


class LLMClient:

    def __init__(self):

        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is missing."
            )

        self.client = Groq(
            api_key=GROQ_API_KEY
        )


    def ask(self, prompt):
        """
        Public interface used by AnswerAgent.
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        SYSTEM_PROMPT
                        + ANTI_HALLUCINATION_PROMPT
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0,
        )

        return response.choices[0].message.content


    def generate(self, prompt):
        """
        Backward-compatible alias.
        """

        return self.ask(prompt)