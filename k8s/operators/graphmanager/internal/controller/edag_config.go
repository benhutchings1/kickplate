package controller

type Config struct {
	Namespace        string
	FinaliserPath    string
	DefaultPortpod   int32
	DefaultPodLabels map[string]string
}

func LoadConfig() (config Config, err error) {
	return Config{
		Namespace:        "default",
		FinaliserPath:    "graph.kickplate.com/finalizer",
		DefaultPortpod:   8000,
		DefaultPodLabels: map[string]string{},
	}, nil
}
