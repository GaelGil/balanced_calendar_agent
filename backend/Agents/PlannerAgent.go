package agents

import (
	"fmt"
	"log"
)

// Assume Plan is already defined somewhere
type Plan struct {
	// Your fields here
}

// LLM is an interface for the LLM client
type LLM interface {
	Parse(model string, input []map[string]string, tools []Tool, format interface{}) (interface{}, error)
}

// Tool represents a single tool for the LLM
type Tool struct {
	// Add fields based on what your tool needs
}

// PlannerAgent is the equivalent of the Python class
type PlannerAgent struct {
	modelName string
	devPrompt string
	llm       LLM
	messages  []map[string]string
	tools     []Tool
}

// NewPlannerAgent is the constructor
func NewPlannerAgent(devPrompt string, llm LLM, messages []map[string]string, tools []Tool, modelName string) *PlannerAgent {
	if modelName == "" {
		modelName = "gpt-4.1-mini"
	}

	agent := &PlannerAgent{
		modelName: modelName,
		devPrompt: devPrompt,
		llm:       llm,
		messages:  messages,
		tools:     tools,
	}

	if devPrompt != "" {
		agent.messages = append(agent.messages, map[string]string{
			"role":    "developer",
			"content": devPrompt,
		})
	}

	return agent
}

// AddMessages adds a user message to the list
func (p *PlannerAgent) AddMessages(query string) {
	p.messages = append(p.messages, map[string]string{
		"role":    "user",
		"content": query,
	})
}

// Plan builds a detailed plan using the LLM
func (p *PlannerAgent) Plan(query string) (*Plan, error) {
	p.AddMessages(query)

	response, err := p.llm.Parse(
		p.modelName,
		p.messages,
		p.tools,
		&Plan{},
	)
	if err != nil {
		log.Printf("LLM parse error: %v", err)
		return nil, err
	}

	plan, ok := response.(*Plan)
	if !ok {
		return nil, ErrInvalidResponse
	}
	return plan, nil
}

// ErrInvalidResponse is returned if the LLM response can't be cast to Plan
var ErrInvalidResponse = fmt.Errorf("invalid response type from LLM")
