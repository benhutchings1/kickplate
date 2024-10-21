package graphvalidate

type Stack struct {
	content []string
	Length  int
}

func NewStack() *Stack {
	var stack Stack
	stack.content = []string{}
	stack.Length = 0
	return &stack
}

func (s *Stack) PushMany(items []string) {
	s.content = append(s.content, items...)
	s.Length += len(items)
}

func (s *Stack) Push(item string) {
	s.content = append(s.content, item)
	s.Length += 1
}

func (s *Stack) Pop() string {
	popIdx := len(s.content) - 1
	popped := s.content[popIdx]
	s.content = s.content[:popIdx]
	s.Length -= 1
	return popped
}
