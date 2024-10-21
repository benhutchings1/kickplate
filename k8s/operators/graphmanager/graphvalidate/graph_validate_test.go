package graphvalidate

import "testing"

func TestShouldValidateGraph(t *testing.T) {
	sampleValidGraph := map[string][]string{
		"a": {"b"},
		"b": {"c", "e"},
		"c": {},
		"d": {"c"},
		"e": {},
	}
	if err := ValidateGraph(sampleValidGraph); err != nil {
		t.Errorf("raised an error on valid graph")
	}
}

func TestShouldRaiseErrorOnCyclicalGraph(t *testing.T) {
	sampleCyclicalGraph := map[string][]string{
		"a": {"b"},
		"b": {"c", "e"},
		"c": {},
		"d": {"c"},
		"e": {"a"},
	}
	if err := ValidateGraph(sampleCyclicalGraph); err == nil {
		t.Errorf("should have raised an error on invalid cyclical graph")
	}
}

func TestShouldRaiseErrorOnGraphWithMissingEdge(t *testing.T) {
	sampleCyclicalGraph := map[string][]string{
		"a": {"b"},
		"b": {"c", "e"},
		"c": {},
		"d": {"c"},
	}
	if err := ValidateGraph(sampleCyclicalGraph); err == nil {
		t.Errorf("should have raised an error on invalid graph with missing edges")
	}
}

func TestShouldAllowManyDisjointValidGraph(t *testing.T) {
	sampleCyclicalGraph := map[string][]string{
		"a": {"b"},
		"b": {},
		"c": {"b"},
		"d": {"b"},
		"e": {"b"},
	}
	if err := ValidateGraph(sampleCyclicalGraph); err != nil {
		t.Errorf("Raised error on valid graph")
	}
}
