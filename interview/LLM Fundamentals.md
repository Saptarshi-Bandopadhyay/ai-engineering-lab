1. What are foundation models, and how have they changed AI engineering?
	Foundation models are large neural networks trained on massive amounts of broad,
	general-purpose data using self-supervised learning. Instead of being built for one
	specific task, they learn general representations of language, images, code, or multiple
	modalities.
	
	They serve as a foundation that can later be adapted for many downstream tasks such
	as question answering, summarization, translation, coding, or document search
	through prompting, fine-tuning, or retrieval.
	
	They have fundamentally changed AI engineering because we no longer train models
	from scratch for every problem. Instead, we build applications around pretrained
	models using techniques like prompt engineering, RAG, tool calling, structured
	outputs, agents, and fine-tuning only when necessary. This has shifted the focus from
	model training to designing reliable AI systems.
	
	Follow-up
	- What makes them "general purpose"?
	- Why self-supervised learning?
	- Examples besides GPT?
	
2. What is a Large Language Model (LLM), and how does it work?
	A Large Language Model is a Transformer-based neural network trained to predict the
	next token in a sequence. During pretraining, it learns statistical patterns, grammar,
	reasoning, facts, and relationships from enormous text datasets.

	When given a prompt, the text is first tokenized into tokens. These tokens are
	converted into embeddings, positional information is added, and they pass through
	multiple Transformer layers containing self-attention and feed-forward networks.
	
	The model produces a probability distribution over the vocabulary for the next token.
	One token is selected using decoding strategies such as greedy decoding, beam
	search, or sampling. This process repeats until the response is complete.
	
	Follow-up
	- Why next-token prediction works so well?
	- Difference between training and inference?
    
3. Inside ChatGPT: What Happens After You Hit Enter?
	When a user submits a prompt, several stages occur:
	1. The input is tokenized.
	2. Tokens are converted into embeddings.
	3. Positional encodings preserve word order.
	4. The embeddings pass through many Transformer layers.
	5. Self-attention determines which previous tokens are most relevant.
	6. Feed-forward networks further transform the representations.
	7. The model outputs probabilities for the next token.
	8. A decoding algorithm selects the next token.
	9. The new token is appended to the context.
	10. The process repeats until an end token or maximum length is reached.
	
	In production systems like ChatGPT, additional components may exist such as safety
	filters, tool calling, retrieval, memory systems, structured output validation, and
	streaming tokens back to the user.
	
	 Follow-up
	- Where does RAG fit?
	- Where does tool calling happen?
    
4. What is the Transformer architecture and how does it work?
	The Transformer is a neural network architecture introduced in the paper _Attention Is
	All You Need_. Unlike RNNs, it processes all tokens in parallel using self-attention
	instead of sequentially.

	Each token attends to every other token to understand context and relationships. The
	architecture consists of stacked attention layers and feed-forward networks with
	residual connections and layer normalization.
	
	During training, this parallelism allows much faster computation than recurrent
	models. Transformers also capture long-range dependencies more effectively, making
	them the dominant architecture for modern language models like GPT, Llama, Claude,
	and Gemini.
    
    Follow-up
	- Why did Transformers replace RNNs?
	- What are long-range dependencies?

5. What are the key components of the Transformer architecture?
	The main components are:
	- Token embeddings
	- Positional encoding
	- Multi-head self-attention
	- Feed-forward neural networks
	- Residual connections
	- Layer normalization
	- Output projection layer
	
	In encoder-decoder Transformers like the original architecture, there are encoder
	layers and decoder layers connected by cross-attention.
	
	Decoder-only architectures such as GPT remove the encoder and use masked self
	attention to predict the next token autoregressively.
	
	 Follow-up
	- Why multi-head attention?
	- Why residual connections?
    
6. What is tokenization in LLMs?
	Tokenization is the process of converting raw text into smaller units called tokens that
	the model can process.
	
	A token may represent a whole word, part of a word, punctuation, or even individual
	characters depending on the tokenizer.
	
	For example,
	
	"unbelievable"
	
	may become
	
	"un", "believ", "able"
	
	Each token is mapped to an integer ID before being converted into embeddings.
	
	Subword tokenization helps balance vocabulary size while allowing models to handle
	rare words and different languages efficiently.
	
	Follow-up
	- Why not use characters?
	- Why not use words?
	
7. Explain BPE (Byte Pair Encoding).
	Byte Pair Encoding is a subword tokenization algorithm that starts with individual
	characters and repeatedly merges the most frequently occurring adjacent pairs to
	build a vocabulary.
	
	Frequent words eventually become single tokens, while rare words remain
	combinations of smaller subwords.
	
	For example,
	
	"low"
	
	"lowest"
	
	"lower"
	
	may share common subword tokens like "low".
	
	BPE reduces vocabulary size while improving the model's ability to understand unseen
	or rare words through reusable subword units.
	
	Follow-up
	- Why is BPE better than word-level tokenization?
	- Complexity?
    
8. Explain WordPiece and SentencePiece.
	Both WordPiece and SentencePiece are subword tokenization methods.

	WordPiece, used in models like BERT, builds its vocabulary by selecting merges that
	maximize the likelihood of the training data rather than simply choosing the most
	frequent pair.
	
	SentencePiece differs because it treats the input as a raw character sequence without
	requiring whitespace-based preprocessing. This makes it language-independent and
	particularly useful for languages where word boundaries are unclear, such as Japanese
	or Chinese.
	
	SentencePiece can implement algorithms like BPE or the Unigram Language Model.
	
	Follow-up
	- Why SentencePiece for multilingual models?
	- What is the Unigram model?
	
9. What is positional encoding, and why is it needed in Transformers?
	Self-attention alone does not contain information about the order of tokens because
	it processes all tokens in parallel. Positional encoding injects information about each
	token's position so the model can understand sequence order.
	
	Without positional information, the sentences
	
	"Dog bites man"
	
	and
	
	"Man bites dog"
	
	would appear identical to the attention mechanism.
	
	The original Transformer used fixed sinusoidal positional encodings, while many
	modern models learn positional embeddings or use alternatives like Rotary Positional
	Embeddings (RoPE), which improve handling of longer contexts.
	
	Follow-up
	- Why RoPE?
	- Learned vs sinusoidal?
    
10. What are embeddings?
	 Embeddings are dense numerical vector representations of tokens, words, sentences, or documents that capture semantic meaning.

	Similar concepts have vectors that are close together in embedding space, allowing
	mathematical operations such as similarity search using cosine similarity or dot
	product.
	
	In LLMs, token IDs are first converted into embedding vectors before entering the
	Transformer. Beyond token embeddings, separate embedding models are often used
	in retrieval systems to represent entire documents or queries for vector search in RAG
	applications.
	
	Embeddings are fundamental to semantic search, recommendation systems,
	clustering, and retrieval-augmented generation because they encode meaning rather
	than exact text.
    
11. Explain the Query(Q), Key(K), and Value(V) in attention.
	Query, Key, and Value are three learned vector representations created from each 
	input token through separate linear transformations.
	
	You can think of them like a search system:
	
	- **Query (Q)** represents what the current token is looking for.
	- **Key (K)** represents what information each token contains.
	- **Value (V)** contains the actual information that will be passed forward.
	
	For every token, the model compares its Query with the Keys of all other tokens using 
	a dot product. These similarity scores are normalized with softmax to produce 
	attention weights. The final output is a weighted sum of the Value vectors, allowing 
	each token to gather the most relevant contextual information.
	
	This mechanism enables the model to dynamically focus on different parts of the 
	sequence depending on the context.
	
	Follow-up

	- Are Q, K, and V learned?
	- Why have three different projections instead of one?
	
12. What is self-attention, and how does it work in Transformers?
	Self-attention is the mechanism that allows every token in a sequence to determine 
	which other tokens are most relevant when computing its representation.
	
	Each token generates its own Query, Key, and Value vectors. The Query of one token 
	is compared with the Keys of every token in the sequence to compute attention 
	scores. After applying softmax, these scores become attention weights that determine 
	how much influence each Value vector should have.
	
	The weighted combination of the Value vectors becomes the updated representation 
	of the token.
	
	This allows the model to capture long-range dependencies efficiently and understand 
	context regardless of the distance between words.
	
	Follow-up
	- Computational complexity?
	- Why is it parallelizable?
	
13. What is Cross Attention in Transformers?
	Cross-attention is an attention mechanism where the Query comes from one 
	sequence while the Keys and Values come from another sequence.

	In the original encoder-decoder Transformer, the decoder uses cross-attention to 
	attend to the encoder's output. This allows the decoder to generate output while 
	incorporating information from the encoded input.
	
	For example, in machine translation, the decoder attends to the encoded English 
	sentence while generating the French translation.
	
	Unlike self-attention, where Q, K, and V all come from the same sequence, cross-
	attention connects two different sequences.
	
	Follow-up
	- Does GPT use cross-attention?
	- Where is cross-attention used today?
	
14. Why do we scale the dot product attention by √dₖ in the Transformer architecture?
	The dot product between Query and Key vectors grows larger as their dimensionality 
	increases. Large values passed into the softmax function cause it to become very 
	peaked, making the probabilities close to 0 or 1.
	
	This leads to very small gradients during training, slowing or destabilizing learning.
	
	Dividing the dot product by the square root of the Key dimension, √dₖ, keeps the 
	attention scores in a reasonable range before softmax. This stabilizes training and 
	improves gradient flow.
	
	Follow-up

	- What happens if we don't scale?
	- Why specifically √dₖ?

15. What is causal masking?
	Causal masking prevents a token from attending to future tokens during training and 
	inference.

	When predicting the next token, the model should only have access to previous 
	tokens. A triangular mask is applied to the attention matrix so that positions 
	corresponding to future tokens receive negative infinity before softmax, making their 
	attention weights effectively zero.
	
	This ensures autoregressive generation and prevents information leakage during 
	training.
	
	Decoder-only models such as GPT use causal masking.
	 
	 Follow-up
	- Does BERT use causal masking?
	- Difference between padding mask and causal mask?
    
16. What are multi-head attention mechanisms? Why use multiple attention heads?
    Multi-head attention uses multiple independent attention mechanisms running in
	parallel. Each head has its own learned Query, Key, and Value projections.
	
	Different heads can learn different relationships within the sequence. For example, 
	one head may focus on grammatical structure, another on long-range dependencies, 
	and another on semantic similarity.
	
	The outputs of all heads are concatenated and projected back into a single 
	representation.
	
	Using multiple heads increases the model's ability to capture diverse patterns 
	compared to relying on a single attention mechanism.
	
	Follow-up
	- Why concatenate?
	- Why not one huge head?

17. What are Feed-Forward Networks in LLMs?
	Feed-Forward Networks, or FFNs, are fully connected neural networks applied 
	independently to every token after the attention layer.
	
	A typical FFN consists of two linear layers with a non-linear activation function such as 
	GELU or ReLU between them. The first layer expands the hidden dimension, and the 
	second projects it back to the original size.
	
	While attention allows tokens to exchange information, the FFN performs non-linear 
	transformations on each token's representation, increasing the model's expressive 
	power.
	
	Follow-up
	- Why expand dimensions?
	- Why GELU instead of ReLU?
	
18. What is the context window in LLMs, and why does it matter?
    The context window is the maximum number of input and generated tokens that a
	model can consider at one time.
	
	Everything within this window is available to the attention mechanism. Information 
	outside the window is no longer visible to the model unless it is reintroduced through 
	techniques such as retrieval or memory.
	
	The context window directly affects how much conversation history, documentation, 
	or source code the model can use. Larger context windows improve the model's 
	ability to reason over long documents and maintain context across extended 
	interactions.
	
	Follow-up
	- How do RAG systems overcome context limits?
	- Does larger context always improve quality?
	
19. Why is the context window limited in LLMs?
	The main limitation comes from the self-attention mechanism. Every token attends to 
	every other token, resulting in a computational and memory complexity of O(n²), 
	where n is the sequence length.
	
	As the context window grows, the attention matrix grows quadratically, making 
	inference significantly slower and more memory-intensive.
	
	Modern research addresses this limitation using techniques such as FlashAttention, 
	sparse attention, sliding-window attention, linear attention, recurrent memory, and 
	architectures optimized for long-context processing.
	
	Follow-up
	- Explain FlashAttention.
	- Explain sparse attention.
	
20. What is temperature in the context of LLMs, and how does it affect output?
	Temperature is a decoding parameter that controls the randomness of token selection 
	during text generation.
	
	After the model computes probabilities for the next token, temperature rescales the 
	logits before the softmax function.
	
	- A **low temperature** (e.g., 0–0.3) makes the probability distribution sharper, leading to more deterministic and consistent outputs.
	- A **high temperature** (e.g., 0.8–1.5) flattens the distribution, increasing randomness and creativity.
	
	Temperature does not change the model's knowledge—it only affects how the model 
	samples from its predicted probability distribution.
	
	In production, lower temperatures are typically used for tasks requiring factual 
	accuracy, such as code generation or structured outputs, while higher temperatures 
	are useful for creative writing and brainstorming.
	
	Follow-up
	- Difference between temperature and top-k/top-p sampling?
	- Can temperature be 0?
	- When would you use temperature 0.8 vs 0.2?
	
21. Why is the first token slower than the rest in an LLM?
	The first generated token has the highest latency because the model must process the 
	entire input prompt through all Transformer layers. This stage is called the **prefill 
	phase**. During prefill, the model computes the Query, Key, and Value 
	representations for every input token and stores the Keys and Values in the KV cache.
	
	Once the first token is generated, subsequent tokens enter the **decode phase**. Thanks 
	to the KV cache, the model reuses the previously computed Keys and Values and only 
	needs to compute them for the newly generated token. As a result, generating later 
	tokens is significantly faster than generating the first one.
	Follow-up
	- What is prefill?
	- What is TTFT (Time To First Token)?
	- How does streaming improve user experience?
	
22. Explain Top-p (nucleus) sampling and Top-k sampling. How do they differ?
	Both Top-k and Top-p are sampling strategies used during text generation to balance 
	randomness and quality.
	
	In **Top-k sampling**, the model keeps only the k most probable tokens and samples 
	from that fixed-size set. For example, if k = 50, only the 50 highest-probability tokens 
	are considered.
	
	In **Top-p (nucleus) sampling**, instead of choosing a fixed number of tokens, the model 
	selects the smallest set of tokens whose cumulative probability exceeds a threshold p, 
	such as 0.9. The number of candidate tokens therefore adapts depending on the 
	probability distribution.
	
	Top-p is generally preferred because it adapts dynamically. When the model is 
	confident, only a few tokens are considered. When it is uncertain, more tokens are 
	included, leading to more natural and flexible generation.
	
	 Follow-up
	- Can Top-p and temperature be used together?
	- Why not always use greedy decoding?
	
23. What are logits, and how are they used in text generation?
	Logits are the raw output scores produced by the model before the softmax function 
	is applied. The model outputs one logit for every token in the vocabulary.
	
	These logits are converted into probabilities using softmax. Decoding strategies such 
	as greedy decoding, Top-k, Top-p, and temperature operate on these logits or the 
	resulting probability distribution to select the next token.
	
	During inference, temperature rescales the logits before softmax, changing the shape 
	of the probability distribution without changing the model's underlying knowledge.
	
	### Follow-up
	- Why softmax?
	- Why not output probabilities directly?
	
24. What are skip connections (residual connections) in Transformers?
	Residual connections, also called skip connections, add the input of a layer directly to 
	its output. Instead of learning an entirely new representation, the layer learns a 
	residual modification to the input.
	
	In Transformers, residual connections are applied around both the attention block and 
	the feed-forward network, followed by layer normalization.
	
	They improve gradient flow, reduce the vanishing gradient problem, enable much 
	deeper networks, and make training more stable.
	
	### Follow-up
	- What is the vanishing gradient problem?
	- Why combine residuals with layer normalization?
	
25. What is the difference between open-source and closed-source LLMs? When would you choose one over the other?
	Open-source LLMs provide access to the model weights, allowing developers to run 
	them locally, fine-tune them, and customize them for specific applications. Examples 
	include Llama, Mistral, and Gemma.
	
	Closed-source models, such as GPT-5 or Claude, are accessed through APIs. Their 
	weights are not publicly available, but they often provide strong performance, 
	managed infrastructure, and frequent updates.
	
	I would choose an open-source model when I need full control, on-premise 
	deployment, lower inference costs at scale, or domain-specific fine-tuning.
	
	I would choose a closed-source model when I need state-of-the-art performance, 
	rapid development, managed infrastructure, or advanced capabilities without 
	maintaining my own serving infrastructure.
	
	### Follow-up
	- When would you self-host?
	- What are licensing considerations?

26. What is the difference between encoder-only, decoder-only, and encoder-decoder Transformer architectures?
    The three architectures are designed for different types of tasks.

	**Encoder-only models**, such as BERT, process the entire input bidirectionally. They are 
	best suited for understanding tasks like classification, sentiment analysis, and 
	information extraction.
	
	**Decoder-only models**, such as GPT and Llama, use causal masking to generate text 
	one token at a time. They are optimized for text generation, coding, and 
	conversational AI.
	
	**Encoder-decoder models**, such as T5 and BART, first encode the input and then 
	generate the output using cross-attention. They are well suited for sequence-to-
	sequence tasks such as translation, summarization, and text transformation.
	
	### Follow-up
	- Why doesn't GPT need an encoder?
	- Why does T5 use both?
	
27. What is KV cache, and how does it speed up inference?
	During autoregressive generation, previously generated tokens never change. Without 
	optimization, the model would recompute the Keys and Values for the entire 
	sequence every time it predicts a new token.
	
	The KV cache stores the previously computed Key and Value vectors for all past 
	tokens. When generating the next token, the model computes only the new Query, 
	Key, and Value for that token and reuses the cached Keys and Values from earlier 
	tokens.
	
	This significantly reduces redundant computation, lowers latency, and improves 
	throughput during inference, especially for long conversations.
	
	### Follow-up
	- Why isn't the Query cached?
	- Why does KV cache increase memory usage?

28. What is model distillation, and how is it used with LLMs?
	Model distillation is the process of training a smaller student model to imitate the 
	behavior of a larger teacher model.
	
	Instead of learning only from labeled data, the student learns from the teacher's 
	outputs or probability distributions. This allows the student to retain much of the 
	teacher's knowledge while requiring fewer parameters and less compute.
	
	In LLMs, distillation is commonly used to create lightweight models for edge devices, 
	lower inference costs, reduce latency, and enable deployment in resource-constrained 
	environments.
	
	Follow-up
	- Distillation vs fine-tuning?
	- Distillation vs pruning?

29. What is Mixture of Experts (MoE), and how does it work in models like Mixtral?
	A Mixture of Experts (MoE) model replaces some feed-forward layers with multiple 
	expert networks. Instead of activating every expert for every token, a routing network 
	selects only the most relevant experts for each token.

	For example, in Mixtral 8×7B, there are eight expert feed-forward networks, but 
	typically only the top two experts are activated for each token. This means only a 
	subset of the model's parameters is used during inference.
	
	MoE models achieve high model capacity while keeping the computational cost per 
	token relatively low, allowing them to scale more efficiently than dense models.
	
	### Follow-up
	- What is the router?
	- Why top-2 experts?
	- What is load balancing?

30. What is the difference between dense and sparse models?
	 In a **dense model**, every parameter participates in every forward pass. Models like GPT-2 and Llama are dense architectures, meaning all layers and neurons are active for every token.
	
	In a **sparse model**, only a subset of the parameters is activated for each input. Mixture 
	of Experts models are a common example, where a routing mechanism activates only 
	a few expert networks for each token.
	
	Dense models are generally simpler to train and serve, while sparse models can 
	provide much larger model capacity with similar computational cost per token. 
	However, sparse models introduce additional complexity in routing, balancing expert 
	utilization, and distributed inference.
	
	Follow-up
	- Why are MoE models considered sparse?
	- What challenges do sparse models introduce in distributed serving?
	
31. What is Flash Attention?
	FlashAttention is an optimized implementation of the self-attention algorithm 
	designed to reduce memory usage and improve speed without changing the 
	attention computation itself.
	
	In standard attention, the full attention matrix is materialized in GPU memory, which 
	becomes expensive for long sequences because memory grows quadratically with the 
	sequence length.
	
	FlashAttention avoids storing the entire attention matrix by computing attention in 
	small blocks (tiles), keeping intermediate results in fast on-chip GPU memory such as 
	SRAM and writing only the final outputs back to high-bandwidth memory.
	
	This significantly reduces memory movement, which is often the main bottleneck on 
	modern GPUs, leading to faster training and inference while producing 
	mathematically equivalent results.
	
	### Follow-up
	- Why is memory bandwidth the bottleneck?
	- Does FlashAttention reduce O(n²) complexity?

32. What is Cross-Entropy Loss?
	Cross-Entropy Loss is the objective function commonly used to train classification 
	models, including LLMs.

	During training, the model predicts a probability distribution over the vocabulary for 
	the next token. Cross-entropy measures how different this predicted distribution is 
	from the true target token.
	
	If the model assigns a high probability to the correct token, the loss is low. If it assigns 
	a low probability, the loss is high.
	
	The optimizer minimizes this loss over millions or billions of examples, gradually 
	improving the model's next-token prediction ability.
	
	### Follow-up
	- Why not Mean Squared Error?
	- How is perplexity related to cross-entropy?
	
33. What is Grouped-Query Attention (GQA), and how does it differ from Multi-Head Attention (MHA)?
	 In Multi-Head Attention, every attention head has its own Query, Key, and Value projections.
	
	Grouped-Query Attention reduces memory usage by allowing multiple Query heads 
	to share the same Key and Value projections.
	
	This significantly reduces the size of the KV cache during inference while maintaining 
	most of the quality of standard Multi-Head Attention.
	
	Because KV cache memory is one of the major bottlenecks for serving large language 
	models, GQA is widely used in modern models such as Llama 3 to improve inference 
	efficiency.
	
	### Follow-up
	- Difference between MHA, MQA, and GQA?
	- Why does GQA reduce KV cache size?
	
34. How does Rotary Position Embedding (RoPE) work, and why is it preferred over learned positional embeddings?
	Rotary Position Embedding encodes positional information by applying a position-
	dependent rotation to the Query and Key vectors rather than adding separate 
	positional embeddings.
	
	Because attention depends on the dot product between Queries and Keys, these 
	rotations naturally encode relative positional information while preserving the 
	mathematical properties of attention.
	
	Compared to learned positional embeddings, RoPE generalizes better to longer 
	context lengths than those seen during training and provides stronger performance 
	for long-context reasoning.
	
	For these reasons, RoPE has become the standard positional encoding method in 
	many modern LLMs, including Llama and Mistral.
	
	### Follow-up
	- Relative vs absolute positions?
	- Why rotate Q and K instead of V?
	
35. Explain Layer Normalization
	Layer Normalization normalizes the activations within each individual training 
	example by computing the mean and variance across the hidden features of a layer.
	
	After normalization, learnable scale and bias parameters allow the model to adjust the 
	normalized values.
	
	In Transformers, Layer Normalization stabilizes training, improves gradient flow, and 
	allows very deep networks to converge reliably.
	
	Unlike Batch Normalization, Layer Normalization does not depend on the batch 
	dimension, making it well suited for sequence models and variable batch sizes.
	
	### Follow-up
	- Pre-LN vs Post-LN Transformers?
	- Why not BatchNorm?

36. Explain RMSNorm (Root Mean Square Layer Normalization)
    RMSNorm is a simplified normalization technique used in many modern LLMs.

	Unlike Layer Normalization, RMSNorm does not subtract the mean. Instead, it 
	normalizes activations using only their root mean square value and then applies a 
	learnable scaling parameter.
	
	This reduces computation while providing training stability similar to Layer 
	Normalization.
	
	Models such as Llama and Mistral use RMSNorm because it is computationally more 
	efficient while maintaining strong performance.
	
	### Follow-up
	- Why remove mean subtraction?
	- Why do Llama models use RMSNorm?
	
37. Your LLM keeps ignoring your instructions. How do you make it follow structured output formats?
    I would avoid relying solely on prompting. Instead, I'd combine multiple techniques:
	1. Use a clear system prompt describing the required format.
	2. Define a JSON Schema or structured output specification.
	3. Use constrained decoding or the model's native structured output API if available.
	4. Validate the output against the schema.
	5. Retry with corrective feedback if validation fails.

	In production systems, schema validation is essential because prompts alone cannot 
	guarantee correctly formatted output.
	
	### Follow-up
	- What is constrained decoding?
	- How would you validate JSON?

38. Your LLM-powered tool hits the context window limit on long documents. How do you handle it?
    The solution depends on the use case, but common approaches include:
	- Chunk the document into smaller overlapping sections.
	- Retrieve only the most relevant chunks using embeddings and a vector database (RAG).
	- Summarize earlier sections hierarchically before continuing.
	- Use sliding windows for sequential processing.
	- Use long-context models when appropriate.
	For question-answering over large document collections, I would typically use RAG so 
	that only the most relevant information is sent to the model instead of the entire 
	document.
	
	### Follow-up
	- Why overlap chunks?
	- Why not always summarize?

39. Your LLM does not admit when it does not know the answer. How do you make it say "I don't know"?
	Hallucination can be reduced through a combination of prompting, retrieval, and 
	validation.
	
	I would instruct the model explicitly to answer "I don't know" when the available 
	information is insufficient. If using RAG, I'd require the answer to be grounded only in 
	retrieved documents. If no relevant evidence is retrieved, the model should respond 
	that it does not know.
	
	I would also use confidence thresholds or retrieval relevance scores to determine 
	when to abstain from answering and evaluate this behavior using hallucination-
	focused benchmarks.
	
	### Follow-up
	- Can temperature fix hallucinations?
	- How do you evaluate hallucination?

40. Your LLM generates responses that are too verbose. How do you control response length?
    There are several ways to control response length:

	- Specify concise instructions in the system prompt, such as "answer in three bullet points."
	- Set an appropriate maximum output token limit.
	- Use lower reasoning verbosity if supported by the model.
	- Request summaries instead of detailed explanations.
	- Apply post-processing if responses still exceed the desired length.
	
	In production, I combine prompt engineering with output token limits because 
	prompt instructions alone are not always sufficient.
	
	### Follow-up
	- Difference between `max_tokens` and context window?
	- How would you prevent truncated responses?

41. Your LLM memorized proprietary training data and leaks it in responses. How do you prevent this?
    Preventing data leakage requires safeguards during both training and deployment.

	During training, I would ensure sensitive or proprietary data is excluded or properly 
	licensed. If fine-tuning on internal data, I'd sanitize and deduplicate datasets and 
	avoid exposing confidential information unnecessarily.
	
	During deployment, I would implement output safety filters, prompt injection 
	defenses, and access controls. For enterprise use cases, I would prefer Retrieval-
	Augmented Generation (RAG) over embedding proprietary knowledge directly into 
	model weights, since access to documents can then be controlled through 
	authentication and permissions.
	
	Finally, I would continuously red-team the model by testing for memorization and 
	data extraction attacks.
	
	### Follow-up
	- Why is RAG safer?
	- What is model memorization?

42. Your LLM coding assistant generates outdated code using deprecated libraries. How do you fix it?
    The root cause is that the model's knowledge is limited to its training cutoff.

	I would augment the model with external knowledge instead of relying solely on 
	pretrained parameters. For example, I'd retrieve the latest API documentation using 
	RAG or connect the model to documentation search tools. I would also provide 
	version-specific documentation in the prompt and instruct the model to cite or follow 
	the retrieved references.
	
	For critical workflows, I would validate generated code using linters, tests, or static 
	analysis before presenting it to the user.
	
	### Follow-up
	- Would you fine-tune?
	- Would MCP or tool calling help?

43. Your tokenizer splits important domain terms into meaningless subword pieces. How do you fix it?
	If domain-specific terms are fragmented excessively, the model may struggle to 
	represent them efficiently.
	
	I would first evaluate whether this fragmentation is actually hurting downstream 
	performance. If it is, possible solutions include training a domain-specific tokenizer, 
	extending the vocabulary with frequently occurring domain terms, or continuing 
	pretraining using the updated tokenizer.
	
	For production systems where retraining isn't practical, I would instead rely on 
	retrieval, glossary expansion, or prompt engineering rather than modifying the 
	tokenizer.
	
	### Follow-up
	- Why is changing the tokenizer difficult?
	- When is it worth doing?

44. Your Transformer's KV cache grows too large during long sequence generation. How do you manage memory?
	KV cache memory grows linearly with sequence length, so for very long conversations 
	it can become a bottleneck.
	
	Depending on the application, I would:
	
	- Evict older cache entries that are no longer needed.
	- Periodically summarize earlier conversation history.
	- Use sliding-window attention.
	- Use models with Grouped-Query Attention to reduce KV cache size.
	- Apply KV cache quantization if supported.
	
	The right strategy depends on whether preserving every previous token is essential 
	for the task.

	Follow-up
	- What is KV quantization?
	- Sliding window vs summarization?

45. Your Transformer runs out of memory on long documents due to quadratic self-attention. How do you scale it?
	Standard self-attention has O(n²) memory and computational complexity, so long 
	documents quickly become expensive.
	
	Depending on the application, I would:
	
	- Use FlashAttention to reduce memory movement.
	- Process documents in chunks.
	- Use Retrieval-Augmented Generation instead of passing the full document.
	- Use sparse or sliding-window attention.
	- Use architectures specifically designed for long-context processing.
	
	Rather than increasing context indefinitely, I would minimize the amount of 
	information the model actually needs to process.\
	
	### Follow-up
	- FlashAttention vs sparse attention?
	- Why chunk?

46. Your distilled student model fails on the complex reasoning that the teacher model handled. How do you close the gap?
	Distillation often transfers general behavior well but can lose complex reasoning 
	ability.
	
	I would improve the student by training on higher-quality reasoning traces generated 
	by the teacher, increasing the diversity of the distillation dataset, and including 
	difficult examples where the student currently fails.
	
	If latency allows, I would also consider a hybrid approach where the student handles 
	routine requests and escalates complex reasoning tasks to the teacher model.
	
	### Follow-up
	- What is chain-of-thought distillation?
	- Why doesn't knowledge transfer perfectly?

47. After RLHF alignment, your LLM became safer but lost capability on hard tasks. How do you manage the alignment tax?
	Alignment tax refers to the reduction in model capability that can occur after 
	alignment training.
	
	I would first evaluate whether the degradation is real using benchmark tasks rather 
	than relying on anecdotal examples. If capability has dropped, I would rebalance the 
	training data, improve the preference dataset, and tune the strength of the alignment 
	objective.
	
	The goal is to make the model refuse unsafe requests while preserving performance 
	on legitimate, complex tasks rather than over-refusing.
	
	### Follow-up
	- How would you measure alignment tax?
	- What causes over-refusal?

48. Your RLHF-trained LLM is gaming the reward model instead of being genuinely helpful. How do you fix reward hacking?
	Reward hacking occurs when the model learns to maximize the reward model without 
	actually improving user outcomes.
	
	I would strengthen the reward model using more diverse human preference data, 
	regularly retrain it, and evaluate the model on held-out benchmarks that are difficult 
	to game. I would also use multiple evaluation signals rather than relying on a single 
	reward model and include human evaluation for high-risk tasks.
	
	The objective is to optimize for genuine helpfulness rather than the reward model 
	itself.
	
	### Follow-up
	- What is reward overoptimization?
	- Why use multiple reward models?

49. Your chatbot loses context after 10 turns in a conversation. How do you maintain a long conversation context?
	I would avoid continually appending the entire conversation because that eventually 
	exceeds the context window and increases latency.
	
	Instead, I would maintain conversational memory using a combination of techniques:
	
	- Keep recent turns in the prompt.
	- Periodically summarize older conversation history.
	- Store important facts in long-term memory or a vector database.
	- Retrieve only relevant past information when needed.
	
	This keeps prompts compact while preserving important context over long 
	conversations.
	
	### Follow-up
	- Conversation buffer vs summary memory?
	- How would LangGraph help?
	- 
50. Your chatbot fails when users switch topics mid-conversation. How do you handle topic switches?
	I would explicitly track conversational state rather than assuming the entire history is 
	always relevant.
	
	When a new user message arrives, I would first classify whether it continues the 
	current topic or starts a new one. If it's a new topic, I would reset or branch the 
	working context while retaining long-term user preferences separately.
	
	For multi-topic assistants, I would maintain conversation state as structured memory 
	or separate threads instead of a single growing prompt. This prevents irrelevant 
	context from interfering with new requests while still allowing the assistant to return 
	to earlier topics if needed.
	
	### Follow-up

	- How would LangGraph model this?
	- How would you detect a topic switch?
	
51. Your QA system always generates an answer even when no answer exists in the context. How do you detect unanswerable questions?
    The goal is to allow the system to abstain instead of hallucinating.

	If I'm using a RAG pipeline, I'd first examine the retrieval stage. If no retrieved 
	document meets a minimum relevance threshold, the system should return "I don't 
	know" or ask the user for more information instead of generating an answer.
	
	I would also instruct the model through the system prompt to answer only using the 
	retrieved context and explicitly state that it should admit when the information is 
	insufficient. Finally, I'd evaluate this behavior using datasets containing unanswerable 
	questions to ensure the system abstains appropriately.
	
	### Follow-up
	- How do you measure retrieval confidence?
	- Would reranking help?
	
52. Your summarization system hallucinated facts not in the original article. How do you fix it?
	 Hallucinations occur when the model generates information that isn't supported by the source.
	
	To reduce this, I would explicitly instruct the model to summarize only the provided 
	text and not introduce external information. I would also use lower-temperature 
	decoding to make the output more deterministic.
	
	For high-stakes applications, I'd add a verification step that compares the generated 
	summary against the source using automated factual consistency metrics or an LLM-
	as-a-judge, and regenerate the summary if unsupported claims are detected.
	
53. Your text generation repeats phrases in long outputs. How do you fix repetition?
	Repetition often results from decoding strategies or long autoregressive generation.
	
	I would adjust decoding parameters by lowering repetition-prone settings, such as 
	using an appropriate temperature together with Top-p sampling. If supported, I'd 
	apply repetition penalties or n-gram blocking to discourage the model from 
	generating the same phrases repeatedly.
	
	I'd also review the prompt to avoid repetitive instructions and evaluate whether the 
	generation length is unnecessarily long.
	
54. Transformers work on text, so can they also understand images?
    Yes. Transformers are not limited to text—they operate on sequences of embeddings.

	In Vision Transformers (ViTs), an image is divided into fixed-size patches. Each patch is 
	converted into an embedding, positional information is added, and the sequence of 
	patch embeddings is processed by the Transformer just like text tokens.
	
	Multimodal models such as GPT-4o, Gemini, and Llama-based vision models combine 
	image encoders with language models so they can understand images, answer visual 
	questions, generate captions, and reason across both text and images.
	
	### Follow-up
	- What is a Vision Transformer?
	- How are image patches tokenized?
	
55. Small Language Models (SLMs)
	Small Language Models are models with significantly fewer parameters than frontier 
	LLMs, typically optimized for lower latency, lower memory usage, and deployment on 
	resource-constrained devices.
	
	While they generally have lower capability than very large models, they are often 
	sufficient for focused tasks such as classification, extraction, lightweight assistants, or 
	on-device inference.

	In production, I would choose an SLM when cost, latency, privacy, or offline 
	deployment are more important than achieving state-of-the-art reasoning 
	performance.
	
	### Follow-up
	- When would you choose Phi or Gemma over a larger model?
	- How does quantization help SLMs?

56. Large Reasoning Models (LRMs)
	Large Reasoning Models are LLMs specifically optimized to perform more deliberate, 
	multi-step reasoning rather than simply generating fluent text.
	
	They are trained and aligned to perform better on tasks involving mathematics, 
	coding, planning, scientific reasoning, and complex decision-making. Compared with 
	standard LLMs, they typically spend more computation during inference to improve 
	reasoning quality.
	
	In practice, I'd use an LRM for tasks where accuracy and reasoning matter more than 
	latency, while using a standard LLM or SLM for simpler conversational or retrieval-
	based tasks.
	
	### Follow-up
	- Why are LRMs slower?
	- When would you not use one?
	
57. What are Autoregressive Models?
	 Autoregressive models generate sequences one token at a time by predicting the next token based only on previously generated tokens.
	
	During training, they learn next-token prediction using causal masking. During 
	inference, each generated token is appended to the context and used to predict the 
	following token.
	
	Modern decoder-only models such as GPT, Llama, and Mistral are autoregressive 
	models because they generate text sequentially in this manner.
	
	### Follow-up
	- Why can't autoregressive models generate all tokens simultaneously?
	- Why use causal masking?

58. Explain the difference between autoregressive and masked language modeling.
    Both are self-supervised learning objectives, but they train models differently.

	**Autoregressive modeling**, used by GPT, predicts the next token using only previous 
	tokens. It uses causal masking and is naturally suited for text generation.
	
	**Masked language modeling**, used by BERT, randomly masks some input tokens and 
	trains the model to predict the missing tokens using both left and right context. 
	Because it sees the full sentence during training, it learns strong bidirectional 
	representations for language understanding tasks.
	
	As a result, autoregressive models excel at generation, while masked language 
	models excel at understanding tasks such as classification and information extraction.
	
	### Follow-up
	- Why is BERT bidirectional?
	- Why isn't GPT bidirectional?

59. Proximal Policy Optimization (PPO)
	Proximal Policy Optimization is a reinforcement learning algorithm commonly used in 
	the RLHF pipeline to align language models with human preferences.
	
	After supervised fine-tuning, a reward model is trained from human preference data. 
	PPO then updates the language model to maximize this reward while restricting how 
	much the policy can change in each update using a clipped objective.
	
	This balance helps improve helpfulness and safety while preventing unstable or 
	excessively large policy updates.
	
	Although PPO played a major role in early RLHF systems, many modern workflows 
	increasingly prefer simpler alignment methods such as Direct Preference 
	Optimization.
	
	### Follow-up
	- Why clipping?
	- PPO vs DPO?

60. Direct Preference Optimization (DPO)
	 Direct Preference Optimization is an alignment method that learns directly from human preference pairs without requiring a separate reinforcement learning stage.
	
	Instead of training a reward model and then optimizing it with PPO, DPO directly 
	adjusts the language model so that preferred responses receive higher probability 
	than rejected responses.
	
	This makes training simpler, more stable, and computationally less expensive while 
	achieving performance comparable to RLHF in many applications.
	
	Because of its simplicity and effectiveness, DPO has become a widely adopted 
	alternative to PPO for preference alignment.
	
	### Follow-up
	- Why is DPO more stable?
	- When would PPO still be useful?

61. Group Relative Policy Optimization (GRPO)
	Group Relative Policy Optimization (GRPO) is a reinforcement learning algorithm 
	developed as an alternative to PPO for aligning large language models. Instead of 
	training a separate reward model and estimating value functions, GRPO generates a 
	group of candidate responses for the same prompt and compares them relative to 
	one another.
	
	The best-performing responses within the group receive higher rewards, while 
	weaker responses receive lower rewards. The model is then updated based on these 
	relative rankings rather than absolute reward estimates.
	
	By eliminating the need for a value model, GRPO simplifies training, reduces 
	computational cost, and improves training stability. This makes it particularly 
	attractive for training large reasoning models.
	
	### Follow-up
	- Why remove the value model?
	- GRPO vs PPO?
	- Why is GRPO popular for reasoning models?

61. Recursive Language Models (RLMs)
	 Recursive Language Models are models designed to improve complex reasoning by solving problems recursively rather than producing an answer in a single forward generation.
	
	Instead of attempting to solve a difficult problem all at once, the model decomposes 
	it into smaller subproblems, solves each one, and recursively combines the 
	intermediate results to produce the final answer.
	
	This approach resembles divide-and-conquer algorithms in computer science and is 
	particularly useful for mathematical reasoning, planning, code generation, and multi-
	step problem solving.
	
	Although recursive reasoning can improve accuracy, it increases inference time 
	because multiple reasoning steps are performed.
	
	### Follow-up
	- How is recursion different from chain-of-thought?
	- When is recursive reasoning useful?
	  
61. Continual Learning in LLMs
	 Continual learning is the ability of a model to acquire new knowledge over time without forgetting previously learned knowledge, a problem known as catastrophic forgetting.
	
	Traditional LLMs have fixed knowledge after training. Updating them usually requires 
	additional fine-tuning, which can degrade previously learned capabilities.
	
	Approaches to continual learning include:
	
	- Continued pretraining on new data.
	- Parameter-efficient fine-tuning methods such as LoRA.
	- Replay methods that mix old and new data.
	- Regularization techniques that protect important parameters.
	- Retrieval-Augmented Generation, which avoids updating model weights by retrieving external knowledge instead.
	
	In production, RAG is often preferred for rapidly changing information because it 
	updates knowledge without retraining the model.
	
	### Follow-up
	- What is catastrophic forgetting?
	- Why choose RAG over continual fine-tuning?
	- How does LoRA help?

61. How do Diffusion Language Models (DLMs) work?
	Diffusion Language Models apply the idea of diffusion, originally developed for 
	image generation, to language generation.
	
	Instead of generating text one token at a time like autoregressive models, diffusion 
	models start with a noisy representation of the entire sequence and iteratively 
	denoise it over multiple steps until coherent text is produced.
	
	Because they refine the whole sequence simultaneously, diffusion language models 
	can revise earlier parts of the output during generation, unlike autoregressive 
	models, which cannot change previously generated tokens.
	
	Potential advantages include better global consistency, improved editing capabilities, 
	and parallel generation. However, diffusion language models currently require 
	multiple denoising steps, making inference slower than standard autoregressive 
	LLMs, so they are still an active area of research.
	
	### Follow-up
	- Autoregressive vs diffusion models?
	- Why are diffusion models common in image generation?
	- What are the inference trade-offs?