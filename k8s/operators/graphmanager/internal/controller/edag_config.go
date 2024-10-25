package controller

type Config struct {
	Namespace     string
	FinaliserPath string
}

func LoadConfig() (config Config, err error) {
	return Config{
		Namespace:     "default",
		FinaliserPath: "graph.kickplate.com/finalizer",
	}, nil
}
