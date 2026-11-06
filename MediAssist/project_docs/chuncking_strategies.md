Chunking Strategies for RAG and the MediAssist AI Design Choice
MediAssist AI project documentation · October 2026

1. Introduction
In a Retrieval-Augmented Generation (RAG) system, documents are not stored or searched as whole files. They are split into smaller pieces called chunks, each chunk is converted into an embedding (a numerical vector), and the vectors are stored in a vector database. When a user asks a question, the system finds the chunks whose meaning is closest to the question and gives them to the language model as context.
Chunking is therefore one of the most important decisions in a RAG pipeline, because it controls what the retriever can find and what the language model gets to read.
• Chunks too large: one chunk mixes several topics, so its embedding becomes vague, retrieval gets less precise, and the prompt fills up with irrelevant text.
• Chunks too small: a chunk loses the context around it (for example, a sentence that says "the patient should do this" without saying what "this" is), so the model receives fragments it cannot interpret.
• Bad boundaries: cutting in the middle of a sentence, a list, or a table row destroys meaning that no later step can recover.
This document explains the main chunking strategies with their definitions, advantages, disadvantages and best-fit scenarios, and then explains why MediAssist AI uses recursive character chunking as its starting strategy.

2. Key concepts and parameters
Chunk size is the maximum length of a chunk. It can be measured in characters, words or tokens. Larger chunks carry more context; smaller chunks give more precise matching.
Chunk overlap is the amount of text repeated between two neighbouring chunks. Overlap protects information that sits near a boundary: if an important sentence is cut between chunk 4 and chunk 5, the overlap means at least one of the chunks still contains it fully. The cost is extra storage and some duplicate results.
Metadata is information attached to each chunk, such as the source file name, page number, section title and chunk index. Metadata is what allows the final answer to show its sources and what allows searches to be filtered, so every strategy below should preserve it.
Separator is a boundary marker (a blank line, a line break, a full stop, a space) used by some splitters to decide where a cut is allowed.

3. Chunking strategies
3.1 Fixed-size chunking
Definition: The text is cut into equal-length pieces (for example every 500 characters or 256 tokens), regardless of what the text says. Overlap is usually added.
How it works: Count characters or tokens, cut at the limit, move forward, repeat.
Pros
• Very simple to implement and to reason about.
• Fast and predictable; chunk sizes are uniform, which makes embedding batches and token budgets easy to manage.
• Works on any text, even text with no structure.
Cons
• Ignores meaning: it can cut words, sentences and lists in half.
• Related ideas get separated, and unrelated ideas get merged.
• Usually gives lower retrieval quality than structure-aware methods.
Best for: quick prototypes, baselines to compare other strategies against, and uniform logs or machine-generated text.
3.2 Sentence-based chunking
Definition: The text is split at sentence boundaries, and consecutive sentences are grouped until a size limit is reached.
Pros
• Every chunk contains complete sentences, so grammar and meaning stay intact.
• Good for question answering where answers are usually one or two sentences.
Cons
• Sentence detection can fail on abbreviations ("Dr.", "mg.", "approx."), numbered lists and clinical shorthand.
• Chunk sizes vary widely, and a single sentence may carry too little context.
• Ignores higher-level structure such as sections and tables.
Best for: clean prose such as articles, FAQs and policy statements written in full sentences.
3.3 Paragraph-based chunking
Definition: The text is split at paragraph breaks (blank lines), so each paragraph, or a small group of paragraphs, becomes a chunk.
Pros
• Paragraphs are natural units of thought, so chunks are usually coherent.
• Easy to implement for well-formatted documents.
Cons
• Paragraph length varies a lot: some are one line, some are several hundred words.
• Extracted PDFs often have unreliable paragraph breaks, so the method can fail silently.
• Very long paragraphs still need a second splitting step.
Best for: well-structured documents such as reports, manuals and policies where paragraphs are consistent.
3.4 Recursive character chunking
Definition: The text is split using an ordered list of separators, from the most meaningful boundary to the least. The splitter first tries to cut at paragraph breaks. If a resulting piece is still larger than the chunk size, it tries line breaks, then sentence endings, then spaces, and only as a last resort cuts by single characters. Small neighbouring pieces are merged back together until the chunk size is reached.
Typical separator order: blank line, line break, full stop with space, space, empty string.
Pros
• Respects natural boundaries whenever possible, but still guarantees that no chunk exceeds the size limit.
• Works on many document types without per-format tuning, including text extracted from PDF, DOCX and TXT.
• Simple, fast, deterministic and cheap: no model calls or embeddings are needed during splitting.
• Well supported and widely used (for example RecursiveCharacterTextSplitter in LangChain), so it is easy to maintain and to hand over to other developers.
• Preserves metadata and supports overlap.
Cons
• It does not understand meaning, so a topic can still be split across two chunks.
• It does not understand document structure such as headings, tables or numbered procedures.
• Tables and forms that were flattened into text may be broken awkwardly.
• Character counts are only an approximation of token counts.
Best for: a strong general-purpose default for mixed document collections, especially when the format and layout of the documents is not fully known in advance.
3.5 Sliding-window chunking
Definition: A window of fixed size moves across the text with a step smaller than the window, so every chunk overlaps heavily with its neighbours (for example a 1,000-character window moving 500 characters at a time).
Pros
• Almost nothing is lost at boundaries, because every passage appears fully in at least one chunk.
• Useful when answers can sit anywhere and exact boundaries are unknown.
Cons
• Large storage and embedding cost because of heavy duplication.
• Retrieval often returns several near-identical chunks, which wastes the model's context.
Best for: short, dense documents where missing a boundary-crossing fact is costly and the data volume is small.
Note that ordinary overlap in fixed-size or recursive chunking is a mild form of this idea; sliding-window usually refers to the heavy-overlap version.
3.6 Semantic chunking
Definition: Sentences are embedded, and a new chunk starts where the meaning shifts, detected by a drop in similarity between neighbouring sentences or groups of sentences.
Pros
• Chunks follow topics instead of arbitrary lengths, so each one is more focused.
• Can improve retrieval precision on long, multi-topic documents.
Cons
• Slower and more expensive, because embeddings are needed during ingestion as well as retrieval.
• Chunk sizes are unpredictable; some may be tiny and some very large.
• Needs a similarity threshold that must be tuned per corpus, and results are harder to debug.
• Gains over simpler methods are not guaranteed and should be measured.
Best for: long narrative documents with clear topic shifts, when retrieval quality justifies the extra cost.
3.7 Structure-aware (document-based) chunking
Definition: The splitter uses the document's own structure: headings, sections, numbered steps, Markdown or HTML tags, page layout. Each section or sub-section becomes a chunk, and the heading path (for example "Discharge Policy > Step 3") is stored as metadata.
Pros
• Chunks match how authors organised the information, so they are coherent and easy to cite.
• Section titles in metadata improve filtering and source attribution.
• Ideal for SOPs, policies and guidelines, which are written as numbered procedures.
Cons
• Requires reliable structure detection; plain PDFs and scanned files often lose their headings during extraction.
• Needs different parsing logic for each file format.
• Sections can be very long or very short, so a secondary size-based split is still needed.
Best for: well-structured technical, legal and procedural documents where headings are preserved in the extracted text.
3.8 Hierarchical (parent-child) chunking
Definition: Documents are split twice. Small "child" chunks are embedded and searched for precision, but when a child matches, the larger "parent" chunk (or the whole section) that contains it is passed to the language model for context.
Pros
• Combines precise matching (small chunks) with rich context (large parents).
• Reduces the problem of retrieving a fragment that is correct but incomplete.
Cons
• More complex to build: two levels of storage and a lookup from child to parent.
• Larger prompts, since parents are longer than the matched child.
• More moving parts to test and maintain.
Best for: long documents where answers depend on surrounding context, such as clinical guidelines and policy manuals.
3.9 Sentence-window retrieval
Definition: Each sentence is embedded individually for very precise matching, but when a sentence is retrieved, the sentences before and after it (the "window") are returned together with it.
Pros
• Very precise retrieval, with surrounding context restored at answer time.
• Simpler than full parent-child indexing.
Cons
• Many more vectors, so storage and indexing cost rise.
• Sentence splitting problems (abbreviations, lists) affect the index directly.
Best for: question answering over prose where answers are short and context just before or after is enough.
3.10 Table-aware chunking
Definition: Tables are detected and handled separately from normal text. A table may be kept whole, split by rows with the header repeated in each chunk, or converted to a description or Markdown form before embedding.
Pros
• Keeps rows, columns and headers together, so numbers are not separated from their labels.
• Important for dosage charts, fee schedules, reference ranges and coding tables.
Cons
• Table detection from PDFs is difficult and often needs specialised parsers.
• Large tables can exceed the chunk size.
• Extra pipeline complexity.
Best for: documents where key facts live in tables, such as billing schedules, lab reference ranges and formularies.
3.11 LLM-based (agentic) chunking
Definition: A language model reads the document and decides where to split, sometimes adding a title or summary to each chunk.
Pros
• Can produce highly coherent chunks and useful summaries.
• Can handle messy or unusual layouts.
Cons
• High cost and latency, and it adds model calls to ingestion.
• Non-deterministic: the same document may be split differently on different runs.
• Risk of the model altering or dropping text.
Best for: small, high-value document sets where quality matters more than cost.

4. Comparison at a glance
Strategy
Respects meaning
Complexity
Cost
Typical best use
Fixed-size
Low
Very low
Very low
Baselines and prototypes
Sentence-based
Medium
Low
Low
Clean prose, FAQs
Paragraph-based
Medium
Low
Low
Well-formatted reports
Recursive character
Medium to high
Low
Low
General-purpose default for mixed documents
Sliding window
Low
Low
Medium to high
Small, dense text where boundary loss is costly
Semantic
High
Medium to high
High
Long multi-topic narrative documents
Structure-aware
High
Medium to high
Low to medium
SOPs, policies, manuals with clear headings
Parent-child
High
High
Medium
Long guidelines needing wide context
Sentence-window
High
Medium
Medium
Precise QA over prose
Table-aware
High (for tables)
High
Medium
Billing, lab and dosage tables
LLM-based
High
High
Very high
Small, high-value collections

5. How to choose a strategy
A practical way to decide:
1. Start simple. Begin with recursive character chunking and measure retrieval quality before adding anything more complex.
2. Look at the documents. If they have strong headings and numbered procedures, add structure-aware splitting. If key facts are in tables, add table-aware handling.
3. Look at the failures. If correct chunks are retrieved but the answers are incomplete, move toward larger context (parent-child or sentence-window). If irrelevant chunks keep appearing, make the chunks smaller or more focused.
4. Measure, do not guess. Build a small set of real questions with known source passages and compare strategies on whether the right chunk appears in the top results.

6. MediAssist AI: project context
MediAssist AI is an enterprise healthcare AI copilot that lets authorised users such as doctors, hospital administrators, front desk staff, insurance teams and clinical operations staff work with healthcare information through one conversational interface. According to the Functional Specification, the system combines enterprise RAG, a multi-agent workflow (planner, retriever, MCP, vision, reasoning, evaluator and response agents), multimodal analysis of uploaded images, MCP-based access to PostgreSQL, an evaluation framework and Azure deployment.
It is important to see where chunking fits in this architecture. The ingestion pipeline is:
Document upload → Parsing → Chunking → Embedding → Vector indexing
Chunking applies to unstructured documents uploaded by users (PDF, DOCX and TXT up to 50 MB), such as SOPs, policies, guidelines and operational manuals, plus uploaded reports. It does not apply to:
• Structured data (patients, appointments, billing, lab results), which stays in PostgreSQL and is reached only through the MCP server tools, as the specification requires.
• Uploaded images (prescriptions, lab report images), which go to the vision agent for OCR and extraction.
The quality of chunking therefore directly affects the RAG half of the product: the retriever agent's vector search, the context given to the reasoning agent, and the source attribution that the specification requires in every answer.

7. Why MediAssist AI uses recursive character chunking
Recursive character chunking was chosen as the initial strategy for the following reasons.
1. The document collection is mixed and its layout is not fully controlled. Users can upload PDF, DOCX and TXT files from different departments. Some will be clean policies, some scanned or exported reports, some plain notes. A strategy that depends on perfect headings or formatting would work on some files and fail on others. Recursive splitting adapts to whatever separators exist in each file.
2. It protects meaning better than fixed-size splitting at almost no extra cost. In healthcare content, a sentence cut in half can change its meaning (a dose, a condition, a warning). Preferring paragraph and line boundaries, then sentences, reduces the chance of splitting an instruction in the middle, while still guaranteeing a maximum chunk size.
3. It is cheap, fast and deterministic. There are no model calls during splitting, so ingestion of large uploads (up to 50 MB) stays fast, costs nothing extra, and gives the same result every time. Deterministic behaviour matters in a healthcare setting where results should be reproducible and auditable.
4. It fits the project's quality and maintainability goals. The specification asks for a modular, config-driven architecture. Recursive chunking is a small, well-understood component with two tunable settings (chunk size and overlap) that can live in configuration, and it is easy to replace later without changing the rest of the pipeline.
5. It preserves the metadata needed for grounding and attribution. The specification requires sources to be displayed with responses and requires metadata filtering in retrieval. The chunker keeps the loader's metadata (source file and page where available) and adds a chunk index, so each retrieved chunk can be traced back to its document.
6. It is a sensible baseline for later comparison. The project has not yet been benchmarked on real MediAssist documents. Starting with a simple, standard strategy gives a reference point; more advanced strategies can then be justified by measured improvements instead of assumptions.

8. MediAssist chunking configuration
Setting
Value
Reason
Splitter
Recursive character splitter (LangChain RecursiveCharacterTextSplitter)
Boundary-aware, general-purpose, widely supported
Chunk size
1,000 characters
Large enough for a complete idea or procedure step, small enough for precise retrieval
Chunk overlap
150 characters
Roughly 15 percent overlap protects sentences near boundaries without heavy duplication
Separator order
blank line, line break, sentence end, space, character
From most meaningful boundary to least
Metadata
Original loader metadata plus a chunk index
Supports source attribution and traceability
The chunker's responsibilities are intentionally limited to: cleaning extracted text (Unicode normalisation, removal of control characters and excess whitespace), skipping empty documents, splitting recursively, keeping existing metadata and adding a chunk index. The proposed location is ingestion/chunker.py, and the intended flow is:
docs = load_documents(uploaded_files) → chunks = chunk_documents(docs)
These values are starting points, not benchmark-validated settings. For dense clinical text, smaller chunks of around 500 to 800 characters sometimes retrieve more precisely, so the values should be tuned after testing.

9. Current implementation status
To keep this document accurate, the status of the chunking work is stated plainly:
• Done: the dashboard and document-upload component exist, and the chunking approach and configuration have been decided.
• Proposed, not yet confirmed: the chunker.py code has been written and reviewed in discussion. It should be treated as implemented only after it is saved in the project, connected to the real document loader, and tested successfully on sample files.
• Still to verify or build: the document loader for PDF, DOCX and TXT, the embedding model choice, the vector store (FAISS or ChromaDB), the retriever and the RAG chain.
Uploading a file in the interface is not the same as parsing it, embedding it and making it searchable; those steps are separate and each needs its own testing.

10. Limitations of the current choice and planned improvements
Recursive character chunking is a good starting point, but it has limits that matter in a healthcare setting.
Limitation
Possible improvement
SOPs and policies have numbered steps and headings that the splitter does not understand
Add structure-aware splitting and store the section title in metadata
Tables such as lab ranges, dosage charts and billing schedules can be broken apart
Add table-aware handling, repeating headers with rows
A retrieved chunk can be correct but incomplete
Consider parent-child retrieval or sentence-window retrieval
Character counts do not match model token counts
Switch to token-based length if prompt budgets become tight
PDF extraction may drop paragraph breaks, weakening the separators
Improve the loader, and use OCR for scanned files
Page numbers can be lost after splitting
Confirm the loader stores page metadata and that it survives chunking
Chunk index restarts are not per file
Count chunks per source file so citations such as "chunk 3 of report.pdf" are possible
These are improvements to consider after the baseline works end to end and has been measured, not requirements for the first version.

11. How to evaluate and tune chunking
Because the specification includes an evaluation framework (retrieval scores, grounding, hallucination detection), chunking should be tested the same way.
1. Build a test set: collect 20 to 50 realistic questions (for example "What is the discharge process?") and note the document and page that contains each answer.
2. Measure retrieval: check whether the correct chunk appears in the top results (hit rate) and how high it ranks.
3. Compare settings: try chunk sizes such as 500, 800 and 1,000 with overlaps of 50, 100 and 150 and compare the results.
4. Inspect failures by hand: read the chunks that were retrieved wrongly and decide whether the cause is chunk size, a bad boundary, a table, or poor extraction.
5. Check answer quality: review grounding and faithfulness of the final answers, not only retrieval scores.
6. Repeat when the data changes: new document types, such as scanned forms or large tables, can justify a different strategy.

12. Summary
Chunking decides what a RAG system can retrieve, so it deserves deliberate choice. There is no single best strategy: fixed-size is the simplest, recursive character chunking balances simplicity and boundary awareness, semantic and LLM-based methods add intelligence at a higher cost, and structure-aware, table-aware and parent-child methods fit specific document types.
MediAssist AI uses recursive character chunking with 1,000 characters and 150 overlap as its starting strategy because the uploaded documents are mixed in format and layout, the method keeps sentences and paragraphs intact where possible, it is fast, free of model calls and reproducible, and it keeps the metadata needed for source attribution. It gives the project a solid, measurable baseline, and the strategy can be upgraded to structure-aware, table-aware or parent-child approaches when testing on real healthcare documents shows where it falls short.