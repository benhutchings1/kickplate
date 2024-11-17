package graphvalidate

import (
	"fmt"
)

// Checks if all connections exist and checks if graph is acyclical
func ValidateGraph(graph map[string][]string) error {
	if err := validateEdgesExist(&graph); err != nil {
		return err
	}

	searchStack := NewStack()
	if err := validateGraphAcyclical(&graph, *searchStack); err != nil {
		return err
	}

	return nil
}

func validateEdgesExist(graph *map[string][]string) error {
	for node := range *graph {
		for _, adjacentNode := range (*graph)[node] {
			if _, exists := (*graph)[adjacentNode]; !exists {
				return fmt.Errorf("cannot make connection %s->%s", node, adjacentNode)
			}
		}
	}
	return nil
}

// Validate if cycles are found in graph
func validateGraphAcyclical(
	graph *map[string][]string, searchStack Stack,
) error {
	allVisited := newVisitedMap(graph)

	for {
		// Find next node not visited
		if nextNode := findDisjointed(allVisited); nextNode != "" {
			// Search that disjointed graph
			if searchedNodes, err := validateSingleGraphAcyclical(
				graph, &searchStack, nextNode,
			); err != nil {
				return err
			} else {
				// Updated visited record
				for _, node := range searchedNodes {
					(*allVisited)[node] = true
				}
			}
		} else {
			// No new nodes found
			return nil
		}
	}
}

func validateSingleGraphAcyclical(
	graph *map[string][]string, searchStack *Stack, startingNode string,
) ([]string, error) {
	visited := newVisitedMap(graph)

	searchStack.Push(startingNode)

	for {
		if len(searchStack.content) == 0 {
			return getVisited(visited), nil
		}
		if discoveredNodes, err := visitNode(
			searchStack.Pop(),
			graph, visited,
		); err != nil {
			return nil, err
		} else {
			searchStack.PushMany(discoveredNodes)
		}
	}
}

func newVisitedMap(graph *map[string][]string) *map[string]bool {
	visited := map[string]bool{}

	for node := range *graph {
		visited[node] = false
	}
	return &visited
}

func visitNode(
	node string,
	graph *map[string][]string,
	visited *map[string]bool,
) ([]string, error) {
	for _, adjacentNodes := range (*graph)[node] {
		if (*visited)[adjacentNodes] {
			return nil, fmt.Errorf("cycle found")
		}
	}

	(*visited)[node] = true
	return (*graph)[node], nil
}

func findDisjointed(visited *map[string]bool) string {
	for node, isVisited := range *visited {
		if !isVisited {
			return node
		}
	}
	return ""
}

func getVisited(visited *map[string]bool) []string {
	wasVisited := []string{}
	for node, isVisited := range *visited {

		if isVisited {
			wasVisited = append(wasVisited, node)
		}
	}
	return wasVisited
}
