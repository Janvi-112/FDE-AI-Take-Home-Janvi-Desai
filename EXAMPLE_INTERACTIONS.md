# Example Interaction Log

This file contains real sample questions and answers returned by the Nexla PDF Query Assistant, demonstrating the system's ability to retrieve grounded, cited answers from the indexed PDF documents.

---

## Interaction 1 — Knowledge Graph Language Model

**Question:**
> What is the use of knowledge graph language model (KGLM)?

**Answer:**
> The primary goal of the knowledge graph language model (KGLM) is to enable a neural language model to generate entities and facts from a knowledge graph (P19-1598.pdf, page 1).

**Sources:**
- P19-1598.pdf, page 0
- P19-1598.pdf, page 1

---

## Interaction 2 — Evaluating Gender Bias

**Question:**
> Can you explain Evaluating of gender bias?

**Answer:**
> The document discusses the evaluation of gender bias in Machine Translation (MT) systems. According to the document, the method of evaluation is an "automatic gender bias evaluation method" (P19-1164.pdf, page 0). This method is based on morphological analysis (e.g., the use of female inflection for the word "doctor") for eight target languages with grammatical gender.
>
> The evaluation method is used to analyze four popular industrial MT systems and two recent state-of-the-art academic MT models. The document states that these models are significantly prone to gender-biased translation errors for all tested target languages.
>
> The analysis shows that these models are more likely to translate based on gender stereotypes rather than more meaningful context (P19-1164.pdf, page 4). The document also notes that recent research has shown that getting rid of these biases can be challenging, but the work presented serves as a first step towards developing more gender-balanced MT models.

**Sources:**
- P19-1164.pdf, page 0
- P19-1164.pdf, page 4

---

## Interaction 3 — Two Tower Model

**Question:**
> How does the Two Tower Model work?

**Answer:**
> According to the document, the Two Tower Model works as follows:
>
> - There are two self-attentional towers, each consisting of N stacked blocks (D19-1539.pdf, page 1).
> - The forward tower operates left-to-right (D19-1539.pdf, page 1).
> - The backward tower operates in the opposite direction (D19-1539.pdf, page 1).
> - Each tower computes the representation for a token based on the representations of the previous layer (D19-1539.pdf, page 1).
> - The representations from the two towers are combined to predict a token, taking care that neither representation contains information about the current target token (D19-1539.pdf, page 1).
> - When predicting the next word, the towers are used individually and the combination module on top is removed. However, the two towers are still jointly trained (D19-1539.pdf, page 6).
> - The combination of losses, including cloze loss and bilm (bi-directional language model) loss, is used to train the model to predict the current word given both left and right context, as well as just left or right context (D19-1539.pdf, page 6).

**Sources:**
- D19-1539.pdf, page 1
- D19-1539.pdf, page 6

---

## Interaction 4 — Automatic Evaluation and Sequence Generation

**Question:**
> How does the automatic evaluation and analysis help with improving sequence generation models?

**Answer:**
> According to the provided document excerpts, automatic evaluation and analysis help improve sequence generation models in the following ways:
>
> 1. **Identifying the "I don't know" problem** — Several authors report the issue that models produce short, generic sentences containing frequent words, as that response can work as a reply in many instances (W18-5713.pdf, page 0).
>
> 2. **Conducting empirical studies** — Researchers have studied unsupervised evaluation metrics for dialogue response generation to better measure and improve model performance (W18-5713.pdf, page 5).
>
> 3. **Comparing model approaches** — The analysis enables direct comparison between retrieval and generation models, helping identify superior approaches through human evaluations (W18-5713.pdf, page 0).

**Sources:**
- W18-5713.pdf, page 0
- W18-5713.pdf, page 5

---

## Interaction 5 - Common Issues with Datasets

**Question:**
> What are some common issues with datasets?

**Answer:**
> According to the text, a common issue with the dataset is:
>
> The language issue: Some of the comments in English dataset contained code-mixed Hindi-English data as well as data from other languages like German.

**Sources:**
- W18-4401.pdf, page 2
- W18-4401.pdf, page 2

---

> **Note:** All answers are grounded exclusively in the indexed PDF documents. The system retrieves the top-6 most relevant chunks via ChromaDB cosine similarity search and passes them to the LLM with strict instructions to cite sources and not hallucinate beyond the provided context.
