1. What is Retrieval-Augmented Generation (RAG), and why is it important?
    Retrieval-Augmented Generation (RAG) is an architecture that combines an LLM with 
    an external knowledge source. Instead of relying only on the model's pretrained 
    parameters, the system retrieves relevant information at inference time and provides 
    it to the model as context before generating a response.

	A typical RAG workflow is:
	
	1. Convert the user's query into an embedding.
	2. Retrieve the most relevant documents from a knowledge base.
	3. Add the retrieved documents to the prompt.
	4. The LLM generates an answer grounded in that context.
	
	RAG is important because it reduces hallucinations, enables access to up-to-date or 
	domain-specific knowledge, avoids retraining when documents change, and allows 
	access control over enterprise data.
	
	### Follow-up
	- Why RAG instead of fine-tuning?
	- What problems does RAG solve?
	  
2. Explain the architecture of a basic RAG system.
    A basic RAG system consists of two stages: indexing and retrieval.

	During **indexing**, documents are collected, cleaned, split into chunks, converted 
	into embeddings using an embedding model, and stored in a vector database along 
	with metadata.
	
	During **retrieval**, the user's query is embedded, similar document chunks are retrieved 
	from the vector database, optionally re-ranked, and inserted into the prompt. The 
	LLM then generates the final response using both the retrieved context and the user's 
	question.
	
	### Follow-up
	- Offline vs online pipeline?
	- Where does reranking fit?
	
3. What are the key components of a RAG pipeline?
    A production RAG pipeline typically includes:
	- Document ingestion
	- Text cleaning and preprocessing
	- Chunking
	- Embedding generation
	- Vector database for indexing
	- Query embedding
	- Retrieval
	- Optional hybrid search and reranking
	- Prompt construction
	- LLM generation
	- Evaluation and monitoring
	
	Each stage contributes to the overall quality of the system. Poor retrieval cannot 
	usually be fixed by a stronger LLM.
	
	### Follow-up
	- Which stage matters most?
	- Where do hallucinations originate?
	  
4. What are chunking strategies, and how do you choose the right chunk size?
	Chunking is the process of splitting large documents into smaller pieces before 
	indexing them.

	The chunk size should balance two competing goals:
	- Smaller chunks improve retrieval precision because each chunk focuses on a single topic.
	- Larger chunks preserve more context but may include irrelevant information.
	
	In practice, the optimal chunk size depends on the document type, embedding model, 
	and application. I would experiment with different chunk sizes and overlaps using 
	evaluation datasets rather than choosing a fixed value arbitrarily.
	
	### Follow-up
	- Why overlap chunks?
	- How would you tune chunk size?
	  
5. Compare fixed-size chunking, semantic chunking, and recursive chunking.
	**Fixed-size chunking** splits text into chunks of a predefined length. It is simple and 
	fast but may split sentences or related ideas.

	**Semantic chunking** attempts to split documents at natural topic or sentence 
	boundaries, producing more meaningful chunks and often improving retrieval quality.
	
	**Recursive chunking** uses a hierarchy of separators, such as paragraphs, sentences, 
	and words, to preserve document structure while respecting the desired chunk size.
	
	In production, recursive chunking is often a good default because it balances 
	structural preservation with size constraints.
	
	### Follow-up
	- When use fixed-size?
	- Recursive vs semantic?
	
6. What are embedding models, and how do they convert text to vectors?
    Embedding models convert text into dense numerical vectors that capture semantic 
    meaning.

	During training, the model learns to place semantically similar text close together in 
	vector space. At inference time, a query and document are converted into vectors, and 
	similarity measures such as cosine similarity are used to retrieve the most relevant 
	documents.
	
	Unlike generative LLMs, embedding models are optimized for semantic 
	representation rather than text generation.
	
	### Follow-up
	- Cosine similarity?
	- Dot product?
	  
7. How do you choose an embedding model for your RAG system?
	I would choose an embedding model based on:

	- Retrieval accuracy.
	- Domain compatibility.
	- Supported languages.
	- Latency.
	- Cost.
	- Embedding dimensionality.
	- Whether the model supports multilingual retrieval if required.
	
	Rather than choosing based on benchmark scores alone, I would evaluate candidate 
	embedding models on the application's own retrieval dataset because the best model 
	depends on the specific use case.
	
	### Follow-up
	- Open-source vs API embeddings?
	- Multilingual embeddings?
	  
8. Explain Agentic RAG.
    Traditional RAG performs a single retrieval before generation.

	Agentic RAG allows an AI agent to reason about the task, decide whether retrieval is 
	needed, perform multiple retrieval steps if necessary, use external tools, evaluate 
	intermediate results, and refine its search before generating the final answer.
	
	Instead of a fixed pipeline, retrieval becomes part of the agent's reasoning process. 
	This enables more complex workflows such as multi-hop question answering, iterative 
	research, and tool-assisted problem solving.
	
	### Follow-up
	- Agentic vs standard RAG?
	- Multi-hop retrieval?
	  
9. What is hybrid search, and why is it better than pure vector search?
    Hybrid search combines dense vector search with traditional keyword-based search, 
    such as BM25.

	Vector search captures semantic similarity, making it effective when the query and 
	document use different wording.
	
	Keyword search excels when exact terms, identifiers, or names are important.
	
	By combining both approaches, hybrid search often achieves better retrieval quality 
	because it benefits from both semantic understanding and exact keyword matching.
	
	### Follow-up
	- BM25?
	- When keyword search wins?
	  
10. What is re-ranking, and how does it improve RAG retrieval quality?
    Re-ranking is a second retrieval stage that reorders the initially retrieved documents 
    using a more accurate but computationally expensive model.

	The first-stage retriever prioritizes speed and returns the top candidate documents. A 
	cross-encoder or reranker then evaluates each query-document pair jointly and 
	produces a more accurate relevance score.
	
	Only the highest-ranked documents are passed to the LLM. This improves retrieval 
	precision, reduces irrelevant context, and often improves answer quality without 
	changing the language mod.
	
	### Follow-up
	- Bi-encoder vs cross-encoder?
	- Why not use cross-encoders for everything?
	  
11. How do you handle multi-document and multi-hop questions in RAG?
	Multi-document questions require combining information from several sources, while 
	multi-hop questions require reasoning across multiple pieces of evidence.
	
	A simple single retrieval step is often insufficient. Instead, I would retrieve a larger 
	candidate set, use reranking to prioritize relevant documents, and allow iterative 
	retrieval where the answer from one retrieval step guides the next.
	
	For complex reasoning tasks, Agentic RAG is often a better approach because the 
	agent can perform multiple retrievals, reason over intermediate results, and synthesize 
	information from multiple documents before generating the final answer.
	
	### Follow-up
	- Multi-hop vs Agentic RAG?
	- When would GraphRAG help?
	  
12. What is the "lost in the middle" problem in RAG systems?
	Even after retrieving the correct documents, LLMs may pay less attention to 
	information located in the middle of a long prompt. As a result, relevant evidence can 
	be overlooked despite being present in the context.
	
	To reduce this problem, I would retrieve fewer but higher-quality chunks through 
	reranking, keep prompts concise, position the most relevant information near the 
	beginning of the context when possible, and avoid sending unnecessary retrieved 
	documents to the model.
	
	### Follow-up
	- Larger context windows?
	- Why reranking helps?
	  
13. How do you evaluate a RAG system? Explain faithfulness, relevance, and context precision/recall.
	Evaluating RAG requires measuring both retrieval quality and generation quality.
	
	**Faithfulness** measures whether the generated answer is supported by the 
	retrieved context rather than containing hallucinated information.
	
	**Relevance** measures whether the final answer actually addresses the user's question.
	
	**Context Precision** measures how much of the retrieved context is actually relevant. 
	High precision means little irrelevant information is retrieved.
	
	**Context Recall** measures whether all the information needed to answer the question 
	was successfully retrieved.
	
	Together, these metrics help identify whether failures come from retrieval or 
	generation rather than evaluating only the final answer.
	
	### Follow-up
	- RAGAS?
	- LLM-as-a-judge?
	  
14. Explain Self-RAG. How does the model decide when to retrieve?
	Self-RAG extends traditional RAG by allowing the model to decide whether retrieval is 
	necessary instead of always retrieving documents.
	
	During generation, the model learns to assess whether additional external knowledge 
	would improve the answer. If retrieval is needed, it retrieves relevant documents, 
	incorporates them into the reasoning process, and can even critique or revise its own 
	output.
	
	This makes retrieval adaptive rather than mandatory, reducing unnecessary retrieval 
	while improving responses that require external knowledge.
	
	### Follow-up
	- Self-RAG vs Agentic RAG?
	- Retrieval policy?
	  
15. What is GraphRAG, and when would you use it over traditional RAG?
	GraphRAG augments traditional retrieval by representing knowledge as a graph of 
	entities and relationships instead of treating documents as isolated chunks.
	
	This enables retrieval based on connected concepts and relationships rather than 
	semantic similarity alone.
	
	I would use GraphRAG for domains where relationships are important, such as 
	knowledge graphs, biomedical research, financial networks, legal reasoning, or 
	enterprise knowledge bases with many interconnected entities.
	
	For straightforward document search, traditional RAG is usually simpler and sufficient.
	
	### Follow-up
	- Graph traversal?
	- Entity extraction?
	  
16. How do you handle structured data (tables, SQL databases) in a RAG pipeline?
	Structured data often requires a different retrieval strategy than unstructured text.
	
	For relational databases, I would translate the user's request into SQL using an LLM or 
	semantic parser, execute the query, and provide the results to the model for 
	explanation or reasoning.
	
	For tables in documents, I would preserve the table structure during ingestion or use 
	specialized table-aware retrieval rather than flattening everything into plain text.
	
	The retrieval method should match the data source rather than forcing every problem 
	into vector search.
	
	### Follow-up
	- SQL agents?
	- Table embeddings?
	  
17. What are the common failure modes of RAG systems, and how do you debug them?
	Common failure modes include:
	
	- Poor chunking.
	- Weak embedding models.
	- Low retrieval precision.
	- Missing relevant documents.
	- Hallucinations despite correct retrieval.
	- Prompt construction errors.
	- Outdated knowledge.
	
	I debug systematically by checking each stage independently:
	
	1. Verify the documents were indexed correctly.
	2. Inspect retrieved chunks.
	3. Evaluate retrieval metrics.
	4. Review prompt construction.
	5. Analyze the LLM output.
	
	This helps identify whether the failure originates from ingestion, retrieval, or 
	generation.
	
	### Follow-up
	- Retrieval failure vs generation failure?
	- Which stage fails most often?
	  
18. How do you handle document updates and maintain freshness in a RAG system?
	I separate the knowledge base from the language model.
	
	When documents change, I reprocess only the updated documents by re-chunking, 
	regenerating embeddings, and updating the corresponding vector database entries 
	rather than rebuilding the entire index.
	
	I would also version documents, remove stale embeddings, schedule incremental 
	indexing, and monitor synchronization between the source documents and the 
	retrieval index.
	
	This allows the system to stay current without retraining the LLM.
	
	### Follow-up
	- Incremental indexing?
	- Versioned documents?
	  
19. How do you optimize RAG for latency in production?
	Latency comes from multiple stages, including embedding generation, vector search, 
	reranking, prompt construction, and LLM inference.
	
	I would optimize each stage by:
	
	- Using efficient embedding models.
	- Choosing an optimized vector database.
	- Limiting retrieval to a reasonable top-k.
	- Applying reranking only to a small candidate set.
	- Caching frequent queries and embeddings.
	- Streaming the LLM response.
	- Using smaller models when appropriate.
	
	Rather than optimizing only the LLM, I'd profile the entire pipeline because retrieval 
	often dominates latency.
	
	### Follow-up
	- Caching embeddings?
	- Why profile first?
	  
20. What is the role of metadata filtering in RAG systems?
	Metadata filtering restricts retrieval to documents matching specific attributes before 
	semantic search is performed.
	
	Metadata may include document type, author, language, department, customer ID, 
	access permissions, creation date, or product version.
	
	Applying metadata filters reduces the search space, improves retrieval precision, 
	lowers latency, and helps enforce security by preventing retrieval of documents the 
	user is not authorized to access.
	
	In enterprise RAG systems, metadata filtering is often essential for both relevance and 
	access control.
	
	### Follow-up
	- ACL filtering?
	- Hybrid filtering?
	  
21. Compare RAG vs fine-tuning. When would you use each?
	RAG and fine-tuning solve different problems.
	
	**RAG** adds external knowledge at inference time by retrieving relevant documents. It's 
	ideal for frequently changing, proprietary, or user-specific information because the 
	knowledge base can be updated without retraining the model.
	
	**Fine-tuning** changes the model's parameters to improve behavior, style, or 
	performance on a particular task. It's useful when the model consistently struggles 
	with a domain-specific task, output format, or reasoning pattern that prompting alone 
	cannot solve.
	
	In practice, I use **RAG to provide knowledge** and **fine-tuning to improve behavior**. 
	They are complementary rather than competing techniques.
	
	### Follow-up
	- Can you combine them?
	- When would RAG be a bad choice?
	  
22. What is query transformation in RAG (HyDE, query decomposition, step-back prompting)?
	Query transformation improves retrieval by rewriting the user's query before 
	searching the knowledge base.
	
	**HyDE (Hypothetical Document Embeddings)** generates a hypothetical answer or 
	document from the query, embeds that generated text, and retrieves documents 
	similar to it. This helps when the user's query is short or ambiguous.
	
	**Query decomposition** breaks a complex question into smaller sub-questions, 
	retrieves information for each one, and combines the results. It's useful for multi-hop 
	reasoning.
	
	**Step-back prompting** first asks a broader or more general question to retrieve high-
	level concepts before returning to the original query, improving retrieval for complex 
	topics.
	
	These techniques improve retrieval quality without changing the underlying 
	knowledge base.
	
	### Follow-up
	- HyDE vs query expansion?
	- When does decomposition help?
	  
23. How do you implement citation and source attribution in RAG?
	During ingestion, I would assign each document chunk metadata such as document 
	ID, title, page number, URL, or section.
	
	After retrieval, I would pass both the content and its metadata to the LLM. The 
	prompt would instruct the model to cite the supporting sources for every factual claim.
	
	In production, I prefer generating citations outside the model whenever possible by 
	attaching references programmatically to the retrieved chunks. This is more reliable 
	than relying solely on the model to produce citations correctly.
	
	### Follow-up
	- Why use metadata?
	- Generated vs programmatic citations?
	  
24. How do you scale a RAG system to millions of documents?
	 Scaling requires optimizing both indexing and retrieval.
	
	I would:
	
	- Use an approximate nearest neighbor (ANN) index instead of exact search.
	- Partition or shard the vector database.
	- Use metadata filtering to reduce the search space.
	- Cache frequent queries and embeddings.
	- Retrieve a small candidate set before reranking.
	- Incrementally update the index rather than rebuilding it.
	
	The goal is to keep retrieval latency low while maintaining retrieval quality as the 
	corpus grows.
	
	### Follow-up
	- HNSW?
	- IVF?
	- Sharding strategies?
	  
25. What is parent-child chunking, and how does it improve retrieval?
	Parent-child chunking indexes small child chunks for precise retrieval while preserving 
	links to larger parent chunks that provide additional context.
	
	During retrieval, the system searches using the child chunks because they are 
	semantically focused. After identifying the relevant child, it returns the corresponding 
	parent chunk to the LLM.
	
	This improves retrieval precision while still giving the model enough surrounding 
	context to generate accurate answers.
	
	### Follow-up
	- Parent-child vs overlap?
	- Why not use large chunks directly?
	  
26. Your RAG system is hallucinating despite having the right context. How do you fix it?
	If the correct context has already been retrieved, the problem is no longer retrieval—
	it's generation.
	
	I would first strengthen the prompt by instructing the model to answer only using the 
	retrieved context and to respond with "I don't know" when the context is insufficient.
	
	I would also reduce unnecessary context, use reranking to surface the most relevant 
	evidence, lower the temperature for factual tasks, and validate the generated answer 
	against the retrieved documents.
	
	If hallucinations persist, I would evaluate whether the chosen model is capable of 
	reliably grounding its responses in the provided context.
	
	### Follow-up
	- Faithfulness metrics?
	- Answer verification?
	  
27. Your RAG chunk overlap causes redundant results. How do you reduce redundancy?
	Chunk overlap preserves context but excessive overlap can cause multiple nearly 
	identical chunks to be retrieved.
	
	I would reduce the overlap size, deduplicate retrieved chunks based on similarity or 
	document IDs, merge overlapping chunks before prompting, and use reranking or 
	Maximal Marginal Relevance (MMR) to promote diversity in the retrieved results.
	
	The objective is to preserve useful context while minimizing redundant information 
	sent to the LLM.
	
	### Follow-up
	- Why overlap?
	- What is MMR?
	  
28. Your RAG retrieval is too slow with a large knowledge base. How do you speed it up?
	I would profile the retrieval pipeline to identify the bottleneck before optimizing.
	
	Common optimizations include using approximate nearest neighbor indexes, 
	metadata filtering, reducing the retrieval candidate set, caching embeddings and 
	frequent queries, optimizing the vector database configuration, and applying 
	reranking only to the top retrieved candidates.
	
	Scaling should focus on maintaining retrieval quality while reducing latency rather 
	than simply retrieving fewer documents.
	
	### Follow-up
	- HNSW?
	- Vector database tuning?
	  
29. Your RAG system returns duplicate results. How do you deduplicate?
	Duplicate retrieval can occur because overlapping chunks or similar documents 
	receive nearly identical similarity scores.
	
	I would deduplicate based on document IDs or content similarity, merge highly 
	overlapping chunks, use diversity-aware retrieval methods such as Maximal Marginal 
	Relevance, and rerank results before constructing the final prompt.
	
	The goal is to maximize information diversity while avoiding repeated context.
	
	### Follow-up
	- MMR?
	- Similarity thresholds?
	  
30. Your RAG system needs per-user access control on internal documents. How do you implement it?
	Access control should be enforced during retrieval rather than generation.
	
	Each indexed document should include metadata describing permissions, such as user 
	IDs, departments, roles, or projects. During retrieval, I would apply metadata filters 
	based on the authenticated user's permissions so that unauthorized documents are 
	never retrieved.
	
	The LLM should only receive documents the user is authorized to access. Security 
	should be enforced by the retrieval layer rather than relying on the model to hide 
	confidential information.
	
	### Follow-up
	- RBAC vs ABAC?
	- Multi-tenant RAG?
	  
31. Your RAG system fails on domain-specific jargon. How do you fix it?
	The first step is to determine whether the problem is in retrieval or generation.
	
	If retrieval is failing, I would evaluate whether the embedding model captures the 
	domain terminology. General-purpose embeddings may not represent specialized 
	vocabulary well, so I would test domain-specific embedding models or continue 
	training embeddings on domain data.
	
	I would also improve ingestion by preserving domain terms during chunking, 
	maintaining glossaries or synonyms, and enriching metadata where appropriate.
	
	If retrieval is already correct but answers remain poor, I would evaluate the LLM itself 
	or consider domain-specific fine-tuning.
	
	I would validate improvements using a benchmark of domain-specific queries rather 
	than relying on anecdotal examples.
	
	### Follow-up
	- Would HyDE help?
	- Domain embeddings vs fine-tuning?
	  
32. Your text-only RAG system now needs to handle images and tables. How do you extend it?
	I would convert the pipeline into a multimodal RAG system.
	
	For images, I would use a vision encoder or a multimodal embedding model so that 
	images can be indexed and retrieved alongside text.
	
	For tables, I would preserve their structure instead of flattening them into plain text. 
	Depending on the use case, I might extract tables into structured formats or use table-
	aware retrieval models.
	
	The retrieval pipeline should become modality-aware so that text, images, and tables 
	are indexed appropriately while the LLM receives all relevant evidence during 
	generation.
	
	### Follow-up
	- Multimodal embeddings?
	- OCR vs vision models?
	  
33. Your RAG knowledge base gets updated frequently and needs versioning. How do you manage it?
	I would version both the source documents and the vector index.
	
	Each document should have metadata such as version number, timestamp, source, 
	and status. When a document changes, only the affected chunks should be 
	reprocessed and re-embedded rather than rebuilding the entire index.
	
	Old versions should either be archived or marked inactive, depending on business 
	requirements. During retrieval, metadata filters can ensure users see either the latest 
	version or a historical version when needed.
	
	This approach supports incremental indexing, auditability, and efficient updates.
	
	### Follow-up
	- Soft delete vs hard delete?
	- Rolling updates?
	  
34. Your RAG system fails on multi-hop questions that require combining multiple facts. How do you fix it?
	Multi-hop reasoning usually requires more than a single retrieval step.
	
	I would decompose the question into smaller sub-questions, retrieve evidence for 
	each one, and combine the retrieved information before generation.
	
	For more complex workflows, I would use Agentic RAG or GraphRAG so that the 
	system can iteratively retrieve additional evidence and reason across multiple 
	documents.
	
	Simply increasing the number of retrieved chunks is usually insufficient because it 
	introduces more irrelevant context.
	
	### Follow-up
	- Query decomposition?
	- GraphRAG?
	  
35. Your enterprise RAG system returns contradictory answers from different source documents. How do you resolve conflicts?
	First, I would preserve source attribution so the system always knows which document 
	supports each claim.
	
	If conflicting information is retrieved, I would rank sources based on trust, recency, or 
	business-defined authority. For example, an official policy document should generally 
	outweigh an outdated internal note.
	
	The prompt should instruct the model to acknowledge conflicting evidence when 
	appropriate rather than inventing a single answer. For critical applications, I would 
	surface the conflicting sources directly to the user instead of hiding the disagreement.
	
	Conflict resolution should be driven by business rules, not left entirely to the language 
	model.
	
	### Follow-up
	- Source ranking?
	- Confidence scoring?
	  
36. Your RAG system returns outdated answers from an evolving knowledge base. How do you keep it current?
	I would separate knowledge updates from model updates.
	
	The knowledge base should be synchronized with the source systems through 
	incremental ingestion pipelines. Updated documents should be re-chunked, re-
	embedded, and replace outdated entries in the vector database.
	
	I would also monitor document freshness, use timestamps in metadata, and prioritize 
	newer documents during retrieval or reranking when recency matters.
	
	This allows the system to stay current without retraining the language model.
	
	### Follow-up
	- Freshness scoring?
	- Real-time indexing?
	  
37. Your RAG system struggles with PDF documents containing tables and layouts. How do you fix PDF parsing?
	PDF parsing should preserve the document's structure rather than extracting plain 
	text alone.
	
	I would use layout-aware document parsing that preserves headings, paragraphs, 
	tables, images, and reading order. Tables should be extracted as structured data, while 
	figures should retain references or captions where relevant.
	
	After parsing, I would chunk the document based on its logical structure rather than 
	fixed character counts. I would also evaluate parsing quality because poor extraction 
	often becomes the root cause of retrieval failures.
	
	For scanned PDFs, I would first apply OCR before the layout-aware parsing step.
	
	### Follow-up
	- OCR vs digital PDFs?
	- Layout-aware parsers?
	- Why does parsing quality affect retrieval?