package controller

type Config struct {
	Namespace        string
	FinaliserPath    string
	DefaultPortpod   int32
	DefaultPodLabels map[string]string
}

func LoadConfig() (config Config) {
	return Config{
		Namespace:        "default",
		FinaliserPath:    "graph.kickplate.com/finalizer",
		DefaultPortpod:   8000,
		DefaultPodLabels: map[string]string{},
	}
}
