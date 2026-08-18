1. What is an AI agent, and how does it differ from a simple LLM call?
	An AI agent is a system built around an LLM that can reason, make decisions, use 
	external tools, maintain state, and execute actions to achieve a goal.
	
	A simple LLM call follows a straightforward pattern: the user provides a prompt, the 
	model generates a response, and the interaction ends.
	
	An AI agent introduces additional capabilities such as planning, tool use, memory, and 
	iterative reasoning. It can observe the environment, decide what action to take next, 
	call APIs or databases, evaluate the results, and continue until the objective is
	achieved.
	
	In other words, an LLM generates text, while an AI agent orchestrates workflows using 
	the LLM as its reasoning engine.
	
	### Follow-up
	- Can every LLM become an agent?
	- Does an agent always need tools?
	  
2. AI Agent Memory
	Agent memory allows an AI system to retain and use information across multiple 
	reasoning steps or conversations.
	
	There are different types of memory:
	
	- **Short-term memory** stores the current conversation or task context.
	- **Long-term memory** stores persistent knowledge such as user preferences or previous interactions.
	- **Working memory** stores intermediate reasoning state while solving a task.
	
	In production systems, memory is often implemented using databases, vector stores, 
	or structured state rather than relying entirely on the model's context window.
	
	Good memory systems help agents maintain continuity, personalize responses, and 
	solve long-running tasks efficiently.
	
	### Follow-up
	- LangGraph memory?
	- Vector memory vs structured memory?
	  
3. Harness Engineering in AI
	Harness engineering refers to building the surrounding infrastructure that allows AI 
	models or agents to be evaluated, tested, monitored, and safely deployed in 
	production.
	
	Rather than focusing only on the model, it includes components such as evaluation 
	datasets, automated testing, prompt versioning, logging, tracing, monitoring, retries, 
	guardrails, and benchmarking.
	
	A good harness enables engineers to measure improvements, reproduce failures, 
	compare different prompts or models, and continuously improve system reliability.
	
	In production AI, the harness is often just as important as the model itself because it 
	ensures the system remains reliable as prompts, models, and workflows evolve.
	
	### Follow-up
	- What belongs in an evaluation harness?
	- How would you test an agent?
	  
4. Explain the ReAct (Reasoning + Acting) agent architecture.
	ReAct combines reasoning and tool use in an iterative loop.
	
	The agent first reasons about the problem, decides whether an external action is 
	required, executes the appropriate tool, observes the result, and then continues 
	reasoning before deciding on the next action.
	
	A typical loop is:
	
	**Thought → Action → Observation → Thought → Final Answer**
	
	This enables the agent to solve problems that require external information or 
	interaction with APIs, databases, search engines, or other tools rather than relying 
	only on its internal knowledge.
	
	### Follow-up
	- ReAct vs function calling?
	- ReAct vs Plan-and-Execute?
	  
5. What is the Plan-and-Execute agent pattern?
	 In the Plan-and-Execute pattern, the agent first creates a high-level plan before performing any actions.
	
	The planning phase decomposes the task into smaller steps. The execution phase 
	then performs each step, using tools when necessary, while monitoring progress and 
	updating the plan if conditions change.
	
	Compared to ReAct, which alternates between reasoning and acting continuously, 
	Plan-and-Execute performs explicit planning first, making it well suited for long or 
	complex workflows.
	
	### Follow-up
	- Dynamic replanning?
	- When use ReAct instead?
	  
6. What is tool use (function calling) in LLMs, and how does it enable agents?
	 Function calling allows an LLM to request the execution of predefined functions instead of generating only natural language.
	
	When the model determines that external information or an action is needed, it 
	outputs a structured function call with the required arguments. The application 
	executes the function, returns the result, and the model incorporates that information 
	into its next response.
	
	This enables agents to interact with APIs, databases, search engines, calendars, file 
	systems, or custom business logic while keeping the language model focused on 
	reasoning rather than directly performing actions.
	
	### Follow-up
	- JSON schema?
	- Tool selection?
	  
7. How do you design and define tools for an AI agent?
	Good tools should perform one well-defined task and have clear inputs and outputs.
	
	When designing tools, I focus on:
	
	- A descriptive name.
	- A clear purpose.
	- Well-defined parameters with validation.
	- Predictable structured outputs.
	- Proper error handling.
	- Minimal required permissions.
	
	I avoid creating overly broad tools because simpler, composable tools make agent 
	reasoning more reliable and easier to debug.
	
	### Follow-up
	- Tool granularity?
	- Tool schemas?
	  
8. What is the difference between single-agent and multi-agent systems?
	A single-agent system uses one agent to solve the entire task.
	
	A multi-agent system consists of multiple specialized agents that collaborate, each 
	focusing on a particular responsibility such as planning, research, coding, verification, 
	or reporting.
	
	Multi-agent systems improve modularity and specialization but introduce additional 
	challenges such as communication, coordination, latency, and conflict resolution.
	
	I would choose a single agent for straightforward workflows and multi-agent systems 
	when tasks naturally divide into specialized roles.
	
	### Follow-up
	- CrewAI?
	- AutoGen?
	- Agent communication?
	  
9. What is Model Context Protocol (MCP), and how does it standardize tool integration?
	 Model Context Protocol (MCP) is an open protocol that standardizes how AI models communicate with external tools, data sources, and services.
	
	Instead of every application implementing custom integrations, MCP defines a 
	common interface through which models can discover available tools, access 
	resources, and invoke capabilities in a consistent way.
	
	This improves interoperability, reduces integration effort, and allows the same agent 
	framework to work with different tool providers without custom code for each one.
	
	In essence, MCP does for AI tools what HTTP does for web communication—it 
	provides a standardized way for systems to interact.
	
	### Follow-up
	- MCP server?
	- MCP client?
	- Resources vs tools?
		  
10. What are AI SubAgents?
	 AI SubAgents are specialized agents that handle specific subtasks within a larger workflow under the coordination of a primary agent.
	
	Instead of one agent performing every responsibility, the main agent delegates work 
	to subagents based on their expertise. For example:
	
	- A research subagent gathers information.
	- A coding subagent writes code.
	- A verification subagent checks correctness.
	- A reporting subagent summarizes the results.
	
	This hierarchical design improves modularity, parallelism, and maintainability while 
	allowing each subagent to use different prompts, tools, or even different language 
	models.
	
	### Follow-up
	- Supervisor agent?
	- Parallel execution?
	- Failure
	  
11. What are the different types of agent memory (short-term, long-term, episodic)?
	AI agents typically use multiple types of memory for different purposes.
	
	**Short-term memory** stores the current task or conversation context and is usually kept in the prompt or execution state.
	
	**Long-term memory** stores persistent information across sessions, such as user preferences, project details, or organizational knowledge. It is often implemented using databases or vector stores.
	
	**Episodic memory** stores records of past interactions or completed tasks, allowing the agent to learn from previous experiences or recall how a similar problem was solved.
	
	Separating these memory types improves scalability because not all information needs to remain in the context window.
	
	### Follow-up
	- Semantic memory?
	- Working memory?
	  
12. How do you handle agent failures and implement error recovery?
    
13. What is an agent loop, and how does it decide when to stop?
    
14. Context Engineering
    
15. How does context compaction work?
    
16. How AI Agents Communicate?
    
17. What are Agent Skills?
    
18. How do you evaluate and test AI agents?
    
19. What are the security risks of agentic systems, and how do you mitigate them?
    
20. What is the difference between reactive and proactive agents?
    
21. How do you manage token consumption and cost in long-running agent workflows?
    
22. What is the human-in-the-loop pattern for agents, and when is it needed?
    
23. How do you implement guardrails for AI agents to prevent harmful actions?
    
24. What is agent reflection, and how does it improve agent performance?
    
25. What is the difference between code-generating agents and tool-calling agents?
    
26. How do you handle multi-modal inputs and outputs in agentic systems?
    
27. How do you implement state management in complex agent workflows?
    
28. How do you build a customer support agent with escalation logic?
    
29. What is agent orchestration, and how do you implement it?
    
30. How do you build a code execution agent safely using sandboxed environments?
    
31. Your AI agent is stuck in an infinite loop. How do you detect and break the cycle?
    
32. Your AI agent gets conflicting answers from different tools. How does it reconcile them?
    
33. Your AI agent burns too many tokens per task. How do you reduce token consumption?
    
34. Your AI agent keeps exceeding its budget per task. How do you enforce budget limits?
    
35. Your AI agent hallucinates tool capabilities and passes wrong inputs. How do you fix it?
    
36. Your AI agent deleted a production database. How do you prevent irreversible actions?
    
37. Your AI agent has many tools, but keeps picking the wrong one. How do you improve tool selection?
    
38. Your AI agent takes too long to complete a task. How do you speed it up?
    
39. Your LLM selects the right tool but extracts the wrong parameters. How do you fix parameter extraction?
    
40. How do Computer-Use Agents work?
    
41. How does LangChain work?
    
42. How does LangGraph work?
    
43. What is OKF (Open Knowledge Format)?
    